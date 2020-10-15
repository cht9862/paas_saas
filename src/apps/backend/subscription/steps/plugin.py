# -*- coding: utf-8 -*-


import abc
from collections import defaultdict
from functools import reduce

import six
from django.db.models import Max, Subquery
from rest_framework import serializers

from apps.backend.plugin.manager import PluginManager
from apps.backend.subscription import constants
from apps.backend.subscription.errors import PluginValidationError
from apps.backend.subscription.tools import (
    create_group_id,
    create_host_key,
    get_all_subscription_steps_context,
    parse_group_id,
    render_config_files,
)
from apps.node_man import constants as const
from apps.node_man.models import (
    GsePluginDesc,
    Host,
    Packages,
    PluginConfigTemplate,
    ProcessStatus,
    SubscriptionStep,
)
from apps.node_man.serializers import misc
from apps.utils import env
from common.log import logger
from pipeline import builder

from ..tools import create_node_id, get_instances_by_scope
from .base import Action, Step


class PluginStepConfigSerializer(serializers.Serializer):
    class ConfigTemplateSerializer(serializers.Serializer):
        name = serializers.CharField(required=True, label="配置文件名")
        version = serializers.CharField(required=True, label="配置文件版本号")
        is_main = serializers.BooleanField(default=False, label="是否主配置")

    plugin_name = serializers.CharField(required=True, label="插件名称")
    plugin_version = serializers.CharField(required=True, label="插件版本")
    config_templates = ConfigTemplateSerializer(default=[], many=True, label="配置模板列表", allow_empty=True)


class PluginStepParamsSerializer(serializers.Serializer):
    port_range = serializers.CharField(label="端口范围", required=False, allow_null=True, allow_blank=True)
    context = serializers.DictField(default={}, label="配置文件渲染上下文")
    keep_config = serializers.BooleanField(label="是否保留原有配置文件", allow_null=True, required=False, default=False)
    no_restart = serializers.BooleanField(label="仅更新文件，不重启进程", allow_null=True, required=False, default=False)


class PluginStep(Step):
    STEP_TYPE = "PLUGIN"

    def __init__(self, subscription_step: SubscriptionStep):
        # 配置数据校验
        config_serializer = PluginStepConfigSerializer(data=subscription_step.config)
        config_serializer.is_valid(raise_exception=True)
        validated_config = config_serializer.validated_data

        params_serializer = PluginStepParamsSerializer(data=subscription_step.params)
        params_serializer.is_valid(raise_exception=True)
        validated_params = params_serializer.validated_data

        # 根据操作系统获取包信息
        plugin_name = validated_config["plugin_name"]
        plugin_version = validated_config["plugin_version"]

        # 更新插件包时的可选项
        self.keep_config = validated_params["keep_config"]
        self.no_restart = validated_params["no_restart"]

        try:
            plugin_desc = GsePluginDesc.objects.get(name=plugin_name)
        except GsePluginDesc.DoesNotExist:
            raise PluginValidationError(msg="插件 [{name}] 信息不存在".format(name=plugin_name))

        if plugin_version != "latest":
            packages = Packages.objects.filter(
                project=plugin_name, version=plugin_version, cpu_arch__in=[const.CpuType.x86_64, const.CpuType.powerpc],
            )
        else:
            newest = (
                Packages.objects.filter(project=plugin_name, cpu_arch__in=[const.CpuType.x86_64, const.CpuType.powerpc])
                .values("os")
                .annotate(max_id=Max("id"))
            )

            packages = Packages.objects.filter(id__in=Subquery(newest.values("max_id")))

        self.package_by_os = {package.os: package for package in packages}
        if not self.package_by_os:
            raise PluginValidationError(
                msg="插件 [{name}-{version}] 不存在".format(name=plugin_name, version=plugin_version)
            )

        # 获取插件配置模板信息
        self.configs = []
        for template in validated_config["config_templates"]:
            is_main_template = template["is_main"]
            if template["version"] != "latest":
                config_template = (
                    PluginConfigTemplate.objects.filter(
                        plugin_version__in=[plugin_version, "*"],
                        name=template["name"],
                        plugin_name=plugin_name,
                        is_main=is_main_template,
                    )
                    .order_by("id")
                    .last()
                )
            else:
                config_template = (
                    PluginConfigTemplate.objects.filter(
                        plugin_version__in=[packages[0].version, "*"],
                        name=template["name"],
                        plugin_name=plugin_name,
                        is_main=is_main_template,
                    )
                    .order_by("id")
                    .last()
                )
            if not config_template:
                if is_main_template:
                    # 不校验主配置模板是否存在是为了兼容老版本插件没有主配置模板
                    continue
                raise PluginValidationError(
                    msg="配置模板 [{name}-{version}] 不存在".format(name=template["name"], version=template["version"])
                )
            # 根据订阅参数，渲染出配置实例
            config_instance = config_template.create_instance(
                data=validated_params["context"], source_app_code=subscription_step.subscription.from_system,
            )
            self.configs.append(config_instance)

        self.target_hosts = subscription_step.subscription.target_hosts

        self.plugin_desc = plugin_desc
        self.plugin_name = plugin_name
        self.plugin_version = packages[0].version

        self.port_range = validated_params.get("port_range")
        super(PluginStep, self).__init__(subscription_step)

    def get_package_by_os(self, os_type):
        try:
            return self.package_by_os[os_type.lower()]
        except KeyError:
            raise PluginValidationError(
                msg="插件 [{name}-{version}] 不支持 {os} 系统".format(
                    name=self.plugin_name, version=self.plugin_version, os=os_type,
                )
            )

    def get_supported_actions(self):
        actions = {
            "MAIN_INSTALL_PLUGIN": MainInstallPlugin,
            "MAIN_STOP_PLUGIN": MainStopPlugin,
            "MAIN_START_PLUGIN": MainStartPlugin,
            "MAIN_RESTART_PLUGIN": MainReStartPlugin,
            "MAIN_RELOAD_PLUGIN": MainReloadPlugin,
            "MAIN_DELEGATE_PLUGIN": MainDelegatePlugin,
            "MAIN_UNDELEGATE_PLUGIN": MainUnDelegatePlugin,
        }
        if self.plugin_desc.is_official:
            # 官方插件是基于多配置的管理模式，安装、卸载、启用、停用等操作仅涉及到配置的增删
            actions.update(
                {
                    "INSTALL": PushConfig,
                    "UNINSTALL": RemoveConfig,
                    "PUSH_CONFIG": PushConfig,
                    "START": PushConfig,
                    "STOP": RemoveConfig,
                }
            )
        else:
            actions.update(
                {
                    "INSTALL": InstallPlugin,
                    "UNINSTALL": UninstallPlugin,
                    "PUSH_CONFIG": PushConfig,
                    "START": StartPlugin,
                    "STOP": StopPlugin,
                }
            )
        return actions

    def get_step_data(self, instance_info, target_host):
        """
        获取步骤上下文数据
        """
        try:
            host = Host.objects.get(inner_ip=target_host["ip"], bk_cloud_id=target_host["bk_cloud_id"])
        except Host.DoesNotExist as error:
            logger.warning("get_step_data error: {}, {}".format(error, str(target_host)))
            return {}

        filter_condition = dict(
            bk_host_id=host.bk_host_id,
            name=self.plugin_name,
            source_id=self.subscription.id,
            source_type=ProcessStatus.SourceType.SUBSCRIPTION,
            proc_type=const.ProcType.PLUGIN,
            group_id=create_group_id(self.subscription, instance_info),
        )
        process_status = ProcessStatus.objects.filter(**filter_condition).last()
        if not process_status:
            filter_condition["version"] = self.plugin_version
            process_status = ProcessStatus.objects.create(**filter_condition)

        control_info = self.generate_plugin_control_info(process_status)
        return {"control_info": control_info}

    def generate_plugin_control_info(self, host_status):
        """
        生成插件控制信息
        """
        package = self.get_package_by_os(host_status.host.os_type)
        control_info = misc.ProcessControlInfoSerializer(instance=package.proc_control).data
        control_info.update(
            gse_agent_home=env.get_gse_env_path("", package.os == const.PluginOsType.windows)["install_path"],
            listen_ip=host_status.listen_ip,
            listen_port=host_status.listen_port,
            group_id=host_status.group_id,
            setup_path=host_status.setup_path,
            log_path=host_status.log_path,
            data_path=host_status.data_path,
            pid_path=host_status.pid_path,
        )
        return control_info

    def check_config_change(self, instance_info, host_status_list):
        """
        检测配置是否有变动
        """
        try:
            for host_status in host_status_list:
                # 渲染新配置
                context = get_all_subscription_steps_context(
                    self.subscription_step, instance_info, host_status.host_info, host_status.name
                )
                rendered_configs = render_config_files(self.configs, host_status, context)
                old_rendered_configs = host_status.configs

                for new_config in rendered_configs:
                    for old_config in old_rendered_configs:
                        if new_config["name"] == old_config["name"] and new_config["md5"] == old_config["md5"]:
                            # 配置一致，开始下一次循环
                            break
                    else:
                        # 如果在老配置中找不到新配置，则必须重新下发
                        return True

        except Exception as e:
            logger.exception("检测配置文件变动失败：%s" % e)
            # 遇到异常也被认为有改动
            return True
        return False

    def make_instances_migrate_actions(self, instances: dict, auto_trigger=False):
        """
        计算实例变化所需要变更动作
        :param instances: dict 变更后的实例列表
        :param auto_trigger: bool 是否自动触发
        :return: dict 需要对哪些实例做哪些动作
        """
        instance_actions = {}
        action = self.subscription_step.config.get("job_type")
        if action:
            # 一次性任务，如指定了action，则对这些实例都执行action动作
            return {instance_id: action for instance_id in instances.keys()}

        id_to_instance_id = {}
        instance_key = "host" if self.subscription.object_type == "HOST" else "service"
        id_key = "bk_host_id" if instance_key == "host" else "id"
        for instance_id, instance in list(instances.items()):
            id_to_instance_id[instance[instance_key][id_key]] = instance_id

        processes = defaultdict(dict)

        statuses = ProcessStatus.objects.filter(
            source_type=ProcessStatus.SourceType.SUBSCRIPTION,
            source_id=self.subscription_step.subscription_id,
            name=self.subscription_step.config["plugin_name"],
        )

        host_map = {
            host.bk_host_id: host
            for host in Host.objects.filter(bk_host_id__in=[status.bk_host_id for status in statuses])
        }

        for status in statuses:
            host = host_map[status.bk_host_id]
            host_key = create_host_key(
                {"bk_supplier_id": const.DEFAULT_SUPPLIER_ID, "bk_cloud_id": host.bk_cloud_id, "ip": host.inner_ip}
            )
            processes[status.group_id][host_key] = status

        if self.subscription.is_main:
            install_action = "MAIN_INSTALL_PLUGIN"
            uninstall_action = "MAIN_STOP_PLUGIN"
            start_action = "MAIN_START_PLUGIN"
            push_config = "MAIN_INSTALL_PLUGIN"
        else:
            install_action = "INSTALL"
            uninstall_action = "UNINSTALL"
            start_action = "START"
            push_config = "PUSH_CONFIG"

        uninstall_ids = []
        max_retry_instance_ids = []

        for group_id, process_status in list(processes.items()):
            _id = int(parse_group_id(group_id)["id"])
            instance_id = id_to_instance_id.get(int(parse_group_id(group_id)["id"]))
            for host_key, host_status in process_status.items():
                if host_status.retry_times > constants.MAX_RETRY_TIME:
                    max_retry_instance_ids.append(instance_id)

            if not instance_id:
                # 如果实例已经不存在，则卸载插件
                uninstall_ids.append(_id)
            else:
                # 获取当前实例需要下发的机器
                if not self.subscription_step.subscription.target_hosts:
                    target_host_keys = [create_host_key(instances[instance_id]["host"])]
                else:
                    target_host_keys = [
                        create_host_key(target_host) for target_host in self.subscription_step.subscription.target_hosts
                    ]

                # 如果需要下发的机器数量与正在运行的进程数量不符
                if len(list(process_status.keys())) != len(target_host_keys):
                    instance_actions[instance_id] = install_action
                    continue

                # 如果运行中进程存在任何异常，则重新下发
                instance_statuses = [status.status for status in list(process_status.values())]
                if const.ProcStateType.UNKNOWN in instance_statuses:
                    instance_actions[instance_id] = install_action
                elif const.ProcStateType.TERMINATED in instance_statuses:
                    instance_actions[instance_id] = start_action

                # 如果配置文件变化，则需要重新下发
                if instance_actions.get(instance_id) in [None, start_action]:
                    is_config_change = self.check_config_change(instances[instance_id], list(process_status.values()))
                    if is_config_change:
                        # 如果实例的配置文件发生变化，则更新配置
                        instance_actions[instance_id] = push_config

        # 如果存在被删除的实例
        if uninstall_ids:
            if self.subscription.object_type == self.subscription.ObjectType.HOST:
                uninstall_scope = {
                    "bk_biz_id": self.subscription.bk_biz_id,
                    "object_type": self.subscription.object_type,
                    "node_type": self.subscription.NodeType.INSTANCE,
                    "nodes": [{"bk_host_id": host_id} for host_id in uninstall_ids],
                }

                uninstall_instances = get_instances_by_scope(uninstall_scope)

                for instance_id in uninstall_instances:
                    instance_actions[instance_id] = uninstall_action
            else:
                for _id in uninstall_ids:
                    instance_id = create_node_id(
                        {
                            "object_type": self.subscription.object_type,
                            "node_type": self.subscription.NodeType.INSTANCE,
                            "id": _id,
                        }
                    )
                    instance_actions[instance_id] = uninstall_action

        for instance_id, instance in list(instances.items()):
            group_id = create_group_id(self.subscription, instance)
            # 如果是新的实例，则安装插件
            if group_id not in processes:
                instance_actions[instance_id] = install_action

        # 自动触发时，重试次数大于 MAX_RETRY_TIME 的实例，不进行操作
        if auto_trigger:
            for instance_id in max_retry_instance_ids:
                instance_actions.pop(instance_id, None)
        else:
            # 非自动触发，把重试次数清零
            statuses.update(retry_times=0)

        return instance_actions


class BasePluginAction(six.with_metaclass(abc.ABCMeta, Action)):
    """
    步骤动作调度器
    """

    # 作业类型
    JOB_TYPE = None

    # 操作类型
    OP_TYPE = None

    # 执行成功后的步骤状态
    SUCCESS_STATE_TYPE = None

    # 动作描述
    ACTION_DESCRIPTION = ""

    def get_plugin_manager(self, target_host):
        """
        根据主机生成插件管理器
        """
        host = Host.get_by_host_info(target_host)
        process_status = self._generate_process_status_record(host)
        package = self.step.package_by_os[host.os_type.lower()]
        plugin_manager = PluginManager(
            host_status=process_status,
            username=self.step.subscription.creator,
            package=package,
            plugin=package.plugin_desc,
            control=package.proc_control,
        )
        return plugin_manager

    def generate_pipeline(self, plugin_manager):
        """
        :param PluginManager plugin_manager:
        :return builder.SubProcess
        """
        start_event = builder.EmptyStartEvent()
        end_event = builder.EmptyEndEvent()

        # 固定流程：停用插件 -> 卸载插件
        activities = self.generate_activities(plugin_manager)

        activities.insert(0, start_event)
        activities.append(plugin_manager.reset_retry_times())
        activities.append(end_event)

        # activity 编排
        reduce(lambda l, r: l.extend(r), [act for act in activities if act])

        sub_process = builder.SubProcess(
            start=start_event,
            name="[{}] {} {}:{}".format(
                self.step.plugin_name,
                self.ACTION_DESCRIPTION,
                plugin_manager.host.bk_cloud_id,
                plugin_manager.host.inner_ip,
            ),
        )
        return sub_process

    @abc.abstractmethod
    def generate_activities(self, plugin_manager):
        """
        :param PluginManager plugin_manager:
        :return list
        """
        return []

    def execute(self, target_host):
        plugin_manager = self.get_plugin_manager(target_host)
        return self.generate_pipeline(plugin_manager)


class MainPluginAction(BasePluginAction):
    def _update_or_create_process_status(self, bk_host_id, group_id, rewrite_path_info):
        return Action._update_or_create_process_status(self, bk_host_id, group_id, rewrite_path_info)


class PluginAction(six.with_metaclass(abc.ABCMeta, BasePluginAction)):
    """
    插件主进程操作
    """

    def _update_or_create_process_status(self, bk_host_id: int, group_id: str, rewrite_path_info: dict):
        """
        :param bk_host_id:
        :param group_id:
        :param rewrite_path_info:
        :return:
        """
        defaults = dict(rewrite_path_info, version=self.step.plugin_version,)
        filter_fields = dict(
            bk_host_id=bk_host_id,
            name=self.step.plugin_name,
            source_id=self.step.subscription.id,
            source_type=ProcessStatus.SourceType.SUBSCRIPTION,
            group_id=group_id,
            proc_type=const.ProcType.PLUGIN,
        )
        host_status = ProcessStatus.objects.filter(**filter_fields).order_by("id").last()
        logger.warning("[_update_or_create_process_status]: {}, {}".format(str(defaults), set(filter_fields)))
        if host_status:
            for key, value in defaults.items():
                setattr(host_status, key, value)
            host_status.save()
        else:
            filter_fields.update(defaults)
            host_status = ProcessStatus.objects.create(**filter_fields)

        return host_status


class InstallPlugin(PluginAction):
    """
    安装插件
    """

    ACTION_NAME = "INSTALL"
    ACTION_DESCRIPTION = "部署插件"

    def generate_activities(self, plugin_manager):
        # 固定流程：下发插件 -> 安装插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.deploy(),
            plugin_manager.install(),
        ]

        # 分配端口
        if plugin_manager.control.listen_port_required and not plugin_manager.host_status.listen_port:
            port_range = self.step.port_range or plugin_manager.control.port_range
            activities.append(plugin_manager.allocate_port(port_range=port_range))

        # 渲染 & 下发插件配置
        if self.step.configs:
            activities.append(
                plugin_manager.render_and_push_config_by_subscription(
                    self.step.subscription_step, self.instance_record.instance_info, self.step.configs,
                )
            )

        # 如果插件需要托管，则重启进程
        if plugin_manager.control.need_delegate:
            activities.append(plugin_manager.reload())

        activities.append(plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING))

        return activities


class MainInstallPlugin(MainPluginAction, InstallPlugin):
    """
    V1.3安装插件
    """

    ACTION_NAME = "MAIN_INSTALL_PLUGIN"
    ACTION_DESCRIPTION = "部署插件程序"

    def generate_activities(self, plugin_manager):
        # 固定流程：下发插件 -> 安装插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.deploy(),
            plugin_manager.install(keep_config=self.step.keep_config),
            None
            if self.step.keep_config
            else plugin_manager.render_and_push_config_by_subscription(
                self.step.subscription_step, self.instance_record.instance_info, self.step.configs,
            ),
        ]

        if not self.step.no_restart:
            activities.append(plugin_manager.restart())

        activities.append(plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING))

        return activities


class UninstallPlugin(PluginAction):
    """
    卸载插件
    """

    ACTION_NAME = "UNINSTALL"
    ACTION_DESCRIPTION = "卸载插件"

    def generate_activities(self, plugin_manager):
        # 停用插件 -> 卸载插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.REMOVED),
            # plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.stop(error_ignorable=False) if plugin_manager.control.need_delegate else None,
            plugin_manager.uninstall(),
        ]
        return activities


class PushConfig(PluginAction):
    """
    下发插件配置
    """

    ACTION_NAME = "PUSH_CONFIG"
    ACTION_DESCRIPTION = "下发插件配置"

    def generate_activities(self, plugin_manager):
        # 下发配置 -> 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.render_and_push_config_by_subscription(
                self.step.subscription_step, self.instance_record.instance_info, self.step.configs,
            ),
            plugin_manager.reload() if plugin_manager.control.need_delegate else None,
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class RemoveConfig(PluginAction):
    """
    移除配置，官方插件专用
    """

    ACTION_NAME = "REMOVE_PLUGIN_CONFIG"
    ACTION_DESCRIPTION = "移除插件配置"

    def generate_activities(self, plugin_manager):
        # 移除配置 -> 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.REMOVED),
            # plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.remove_config() if plugin_manager.host_status.configs else None,
            plugin_manager.reload(error_ignorable=False) if plugin_manager.control.need_delegate else None,
        ]
        return activities


class StartPlugin(PluginAction):
    """
    启动插件
    """

    ACTION_NAME = "START"
    ACTION_DESCRIPTION = "启动插件进程"

    def generate_activities(self, plugin_manager):
        # 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.start() if plugin_manager.control.need_delegate else None,
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class MainStartPlugin(MainPluginAction, StartPlugin):
    pass


class MainReStartPlugin(MainPluginAction, StartPlugin):
    ACTION_NAME = "RESTART"
    ACTION_DESCRIPTION = "重启插件进程"

    def generate_activities(self, plugin_manager):
        # 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.restart() if plugin_manager.control.need_delegate else None,
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class StopPlugin(PluginAction):
    """
    停用插件
    """

    ACTION_NAME = "STOP"
    ACTION_DESCRIPTION = "停止插件进程"

    def generate_activities(self, plugin_manager):
        # 停止插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.stop(error_ignorable=False) if plugin_manager.control.need_delegate else None,
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.TERMINATED),
        ]
        return activities


class MainStopPlugin(MainPluginAction, StopPlugin):
    pass


class ReloadPlugin(PluginAction):
    """
    重载插件
    """

    ACTION_NAME = "RELOAD_PLUGIN"
    ACTION_DESCRIPTION = "重载插件"

    def generate_activities(self, plugin_manager):
        # 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.reload(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class MainReloadPlugin(MainPluginAction, ReloadPlugin):
    pass


class DelegatePlugin(PluginAction):
    """
    托管插件
    """

    ACTION_NAME = "DELEGATE_PLUGIN"
    ACTION_DESCRIPTION = "托管插件"

    def generate_activities(self, plugin_manager):
        # 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.delegate(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class MainDelegatePlugin(MainPluginAction, DelegatePlugin):
    pass


class UnDelegatePlugin(PluginAction):
    """
    取消托管插件
    """

    ACTION_NAME = "UNDELEGATE_PLUGIN"
    ACTION_DESCRIPTION = "取消托管插件"

    def generate_activities(self, plugin_manager):
        # 重启插件
        activities = [
            plugin_manager.check_agent_status(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.UNKNOWN),
            plugin_manager.undelegate(),
            plugin_manager.set_process_status(plugin_manager.ProcessStatus.RUNNING),
        ]
        return activities


class MainUnDelegatePlugin(MainPluginAction, UnDelegatePlugin):
    pass
