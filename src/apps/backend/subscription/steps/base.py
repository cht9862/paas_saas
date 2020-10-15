# -*- coding: utf-8 -*-


import abc
import ntpath
import posixpath

from apps.backend.subscription.errors import PluginValidationError
from apps.backend.subscription.tools import create_group_id
from apps.node_man import constants as const
from apps.node_man.models import ProcessStatus, SubscriptionStep


class Step(object, metaclass=abc.ABCMeta):
    """
    步骤基类
    """

    STEP_TYPE = ""

    def __init__(self, subscription_step: SubscriptionStep):
        """
        :param models.SubscriptionStep subscription_step: 订阅步骤
        """
        self.subscription_step = subscription_step

        # shortcut
        self.step_id = subscription_step.step_id
        self.subscription = subscription_step.subscription

    def get_supported_actions(self):
        """
        获取插件支持的动作列表，键值对：{action_name: action_cls}
        """
        return {}

    def create_action(self, action_name, instance_record):
        """
        获取步骤的动作处理类
        :param action_name: 动作名称
        :param instance_record: 订阅实例执行记录
        :rtype: Action
        """
        for name, action_cls in self.get_supported_actions().items():
            if name == action_name:
                return action_cls(action_name, self, instance_record)
        raise ValueError("action [%s] is not registered" % action_name)

    @abc.abstractmethod
    def make_instances_migrate_actions(self, instances, auto_trigger=False):
        """
        计算实例变化所需要变更动作
        :param instances: list 变更后的实例列表
        :param auto_trigger: bool 是否自动触发
        :return: dict 需要对哪些实例做哪些动作
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_step_data(self, instance_info, target_host):
        """
        根据当前实例及目标机器，获取步骤上下文数据数据
        """
        raise NotImplementedError

    def get_all_step_data(self, instance_info, target_host):
        from apps.backend.subscription.steps import StepFactory

        all_step_data = {
            step.step_id: StepFactory.get_step_manager(step).get_step_data(instance_info, target_host)
            for step in self.subscription.steps
        }
        return all_step_data


class Action(object, metaclass=abc.ABCMeta):
    """
    步骤动作调度器
    """

    # 动作描述
    ACTION_DESCRIPTION = ""

    def __init__(self, action_name, step, instance_record):
        """
        :param Step step: 步骤实例
        :param models.SubscriptionInstanceRecord instance_record: 订阅实例执行记录
        """
        self.step = step
        self.instance_record = instance_record
        self._set_step_data({"action": action_name})

    def _get_step_data(self):
        return self.instance_record.get_step_data(self.step.step_id)

    def _set_step_data(self, data):
        self.instance_record.set_step_data(self.step.step_id, data)

    def set_pipeline_id(self, pipeline_id):
        self._set_step_data({"pipeline_id": pipeline_id})

    def get_action_status(self):
        return self._get_step_data()["status"]

    def set_action_status(self, status):
        self._set_step_data({"status": status})

    def get_group_id(self):
        """
        获取插件组ID
        """
        return create_group_id(self.step.subscription, self.instance_record.instance_info)

    def get_extra_info(self):
        return self._get_step_data()["extra_info"].get(self.get_group_id())

    def set_extra_info(self, extra_info):
        self._set_step_data({"extra_info": {self.get_group_id(): extra_info}})

    def get_all_step_data(self):
        """
        获取所有步骤的上下文信息
        """
        all_extra_info = {}
        all_step_data = self.instance_record.get_all_step_data()
        for step_data in all_step_data:
            all_extra_info[step_data["id"]] = step_data["extra_info"].get(self.get_group_id())
        return all_extra_info

    @abc.abstractmethod
    def execute(self, target_host):
        raise NotImplementedError

    def _generate_process_status_record(self, host):
        """
        根据目标主机生成主机进程实例记录
        :param host: Host
        :return: HostStatus
        """
        group_id = self.get_group_id()

        try:
            package = self.step.package_by_os[host.os_type.lower()]
        except KeyError:
            raise PluginValidationError(
                msg="插件 [{name}-{version}] 不支持 {os} 系统".format(
                    name=self.step.plugin_name, version=self.step.plugin_version, os=host.os_type,
                )
            )

        # 配置插件进程实际运行路径配置信息
        if package.os == const.PluginOsType.windows:
            path_handler = ntpath
        else:
            path_handler = posixpath

        if package.plugin_desc.category == const.CategoryType.external:
            # 如果为 external 插件，需要补上插件组目录
            setup_path = path_handler.join(
                package.proc_control.install_path, "external_plugins", group_id, package.project,
            )
            log_path = path_handler.join(package.proc_control.log_path, group_id)
            data_path = path_handler.join(package.proc_control.data_path, group_id)
            pid_path_prefix, pid_filename = path_handler.split(package.proc_control.pid_path)
            pid_path = path_handler.join(pid_path_prefix, group_id, pid_filename)
        else:
            setup_path = path_handler.join(package.proc_control.install_path, "plugins", "bin")
            log_path = package.proc_control.log_path
            data_path = package.proc_control.data_path
            pid_path = package.proc_control.pid_path

        rewrite_path_info = {
            "setup_path": setup_path,
            "log_path": log_path,
            "data_path": data_path,
            "pid_path": pid_path,
        }
        host_status = self._update_or_create_process_status(host.bk_host_id, group_id, rewrite_path_info)

        return host_status

    def _update_or_create_process_status(self, bk_host_id, group_id, rewrite_path_info):
        if self.step.subscription.is_main:
            source_id = self.step.subscription.id
            source_type = ProcessStatus.SourceType.SUBSCRIPTION
        else:
            source_id = None
            source_type = ProcessStatus.SourceType.DEFAULT
            group_id = ""
        host_status, is_created = ProcessStatus.objects.get_or_create(
            bk_host_id=bk_host_id,
            name=self.step.plugin_name,
            source_id=source_id,
            source_type=source_type,
            group_id=group_id,
            proc_type=const.ProcType.PLUGIN,
            defaults=dict(rewrite_path_info, version=self.step.plugin_version,),
        )

        if not is_created:
            for key, value in rewrite_path_info.items():
                setattr(host_status, key, value)
            host_status.version = self.step.plugin_version
            host_status.save()
        return host_status
