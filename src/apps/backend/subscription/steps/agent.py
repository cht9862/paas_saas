# -*- coding: utf-8 -*-

import abc
from functools import reduce

from django.conf import settings
from django.utils.translation import ugettext as _

from apps.backend.agent.manager import AgentManager
from apps.node_man import constants
from apps.node_man.constants import ProcStateType
from apps.node_man.models import GsePluginDesc, Host, SubscriptionStep
from pipeline import builder
from pipeline.builder import Data, NodeOutput, Var
from .base import Action, Step

# 需分发到 PROXY 的文件（由于放到一次任务中会给用户等待过久的体验，因此拆分成多次任务）
FILES_TO_PUSH_TO_PROXY = [
    {"files": ["py36.tgz"], "name": _("检测 BT 分发策略（下发Py36包）")},
    {"files": ["gse_client-windows-x86.tgz", "gse_client-windows-x86_64.tgz"], "name": _("下发 Windows 安装包")},
    {
        "files": ["gse_client-aix-powerpc.tgz", "gse_client-linux-x86.tgz", "gse_client-linux-x86_64.tgz"],
        "name": _("下发 Linux 安装包"),
    },
    {
        "files": [
            "curl-ca-bundle.crt",
            "curl.exe",
            "libcurl-x64.dll",
            "7z.dll",
            "7z.exe",
            "handle.exe",
            "unixdate.exe",
            "tcping.exe",
            "nginx-portable.tgz",
        ],
        "name": _("下发安装工具"),
    },
]


class AgentStep(Step):
    STEP_TYPE = "AGENT"

    def __init__(self, subscription_step: SubscriptionStep):
        self.auto_launch_plugins = GsePluginDesc.get_auto_launch_plugins()
        super(AgentStep, self).__init__(subscription_step)

    def get_package_by_os(self, os_type):
        return

    def get_supported_actions(self):
        supported_actions = [
            InstallAgent,
            ReinstallAgent,
            UninstallAgent,
            UpgradeAgent,
            RestartAgent,
            InstallProxy,
            ReinstallProxy,
            UninstallProxy,
            ReplaceProxy,
            UpgradeProxy,
            RestartProxy,
            ReloadAgent,
            ReloadProxy,
        ]
        return {action.ACTION_NAME: action for action in supported_actions}

    def get_step_data(self, instance_info, target_host):
        """
        获取步骤上下文数据
        """
        return

    def generate_agent_control_info(self, host_status):
        """
        生成Agent控制信息
        """
        return

    def make_instances_migrate_actions(self, instances, auto_trigger=False):
        """
        安装Agent不需要监听CMDB变更
        若有需要按CMDB拓扑变更自动安装Agent的需求，需完善此方法
        """
        instance_actions = {instance_id: self.subscription_step.config["job_type"] for instance_id in instances}
        return instance_actions


class AgentAction(Action, abc.ABC):
    """
    步骤动作调度器
    """

    ACTION_NAME = ""
    # 动作描述
    ACTION_DESCRIPTION = ""

    def get_agent_manager(self):
        """
        根据主机生成Agent管理器
        """
        agent_manager = AgentManager(
            instance_record=self.instance_record,
            creator=self.step.subscription.creator,
            blueking_language=self.step.subscription_step.params.get("blueking_language"),
        )
        return agent_manager

    def generate_pipeline(self, agent_manager):
        """
        :param PluginManager agent_manager:
        :return builder.SubProcess
        """
        start_event = builder.EmptyStartEvent()
        end_event = builder.EmptyEndEvent()

        activities, pipeline_data = self.generate_activities(agent_manager)
        pipeline_data.inputs["${description}"] = Var(type=Var.PLAIN, value=self.ACTION_DESCRIPTION)

        activities.insert(0, start_event)
        activities.append(agent_manager.update_job_status())
        activities.append(end_event)

        # activity 编排
        reduce(lambda l, r: l.extend(r), [act for act in activities if act])

        sub_process = builder.SubProcess(
            start=start_event,
            name="[{}] {} {}:{}".format(
                self.ACTION_NAME,
                self.ACTION_DESCRIPTION,
                agent_manager.host_info["bk_cloud_id"],
                agent_manager.host_info["bk_host_innerip"],
            ),
            data=pipeline_data,
        )
        return sub_process

    @abc.abstractmethod
    def generate_activities(self, agent_manager):
        """
        :param PluginManager agent_manager:
        :return list
        """
        return [], None

    def execute(self, target_host: dict):
        agent_manager = self.get_agent_manager()
        return self.generate_pipeline(agent_manager)

    #
    # def get_plugin_manager(self, plugin_name, host_info):
    #     """
    #     根据主机生成Agent管理器
    #     """
    #     host = Host.get_by_host_info(host_info)
    #     package = self._get_package(plugin_name, host)
    #     process_status = self._generate_process_status_record(host)
    #     plugin_manager = PluginManager(host_status=process_status, username=self.step.subscription.creator,
    #                                    package=package, plugin=package.plugin_desc, control=package.proc_control)
    #     return plugin_manager
    #
    # def _get_package(self, plugin_name, host, plugin_version="latest"):
    #     newest = Packages.objects.filter(
    #         project=plugin_name, cpu_arch=const.CpuType.x86_64
    #     ).values("os").annotate(max_id=Max("id"))
    #
    #     packages = Packages.objects.filter(
    #         id__in=Subquery(newest.values("max_id"))
    #     )
    #
    #     package_by_os = {package.os: package for package in packages}
    #     self.step.package_by_os = package_by_os
    #     self.step.plugin_name = plugin_name
    #     self.step.plugin_version = 'latest'
    #     return package_by_os[host.os_type.lower()]
    #
    # def _get_auto_launched_plugins(self):
    #     auto_launch_plugins = GsePluginDesc.get_auto_launch_plugins()
    #     return auto_launch_plugins


class InstallAgent(AgentAction):
    """
    安装Agent
    """

    ACTION_NAME = "INSTALL_AGENT"
    ACTION_DESCRIPTION = "安装"

    def generate_activities(self, agent_manager: AgentManager):
        register_host = agent_manager.register_host()

        if agent_manager.host_info["is_manual"]:
            self.ACTION_DESCRIPTION = "手动安装"
            install_name = _("手动安装")
        else:
            install_name = _("安装")

        activities = [
            register_host,
            agent_manager.choose_ap(),
            agent_manager.install(install_name),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING),
        ]

        # 把注册 CMDB 得到的bk_host_id 作为输出给到后续节点使用
        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = NodeOutput(
            source_act=register_host.id, source_key="bk_host_id", type=Var.SPLICE, value="",
        )
        pipeline_data.inputs["${is_manual}"] = NodeOutput(
            source_act=register_host.id, source_key="is_manual", type=Var.SPLICE, value=False,
        )

        # 验证类型为TJJ需要查询密码增加在第一步
        if agent_manager.host_info["auth_type"] == constants.AuthType.TJJ_PASSWORD:
            activities.insert(1, agent_manager.query_tjj_password())

        for plugin in self.step.auto_launch_plugins:
            activities.append(agent_manager.delegate_plugin(plugin.name))
        return activities, pipeline_data


class ReinstallAgent(AgentAction):
    """
    重装Agent
    """

    ACTION_NAME = "REINSTALL_AGENT"
    ACTION_DESCRIPTION = "重装"

    def generate_activities(self, agent_manager: AgentManager):

        is_manual = Host.objects.get(bk_host_id=agent_manager.host_info["bk_host_id"]).is_manual
        if is_manual:
            install_name = _("手动安装")
        else:
            install_name = _("安装")

        activities = [
            agent_manager.choose_ap(),
            agent_manager.install(install_name),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING),
        ]

        # 上云增加查询密码原子
        if settings.USE_TJJ:
            activities.insert(0, agent_manager.query_tjj_password())

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])
        for plugin in self.step.auto_launch_plugins:
            activities.append(agent_manager.delegate_plugin(plugin.name))

        return activities, pipeline_data


class UpgradeAgent(ReinstallAgent):
    """
    升级Agent
    """

    ACTION_NAME = "UPGRADE_AGENT"
    ACTION_DESCRIPTION = "升级"

    def generate_activities(self, agent_manager: AgentManager):
        push_upgrade_package = agent_manager.push_upgrade_package()
        activities = [
            push_upgrade_package,
            agent_manager.run_upgrade_command(),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING),
        ]

        pipeline_data = Data()
        pipeline_data.inputs["${package_name}"] = NodeOutput(
            source_act=push_upgrade_package.id, source_key="package_name", type=Var.SPLICE, value="",
        )
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class RestartAgent(AgentAction):
    """
    重启Agent
    """

    ACTION_NAME = "RESTART_AGENT"
    ACTION_DESCRIPTION = "重启"

    def generate_activities(self, agent_manager: AgentManager):
        activities = [
            agent_manager.restart(),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING),
        ]

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class RestartProxy(AgentAction):
    """
    重启Proxy
    """

    ACTION_NAME = "RESTART_PROXY"
    ACTION_DESCRIPTION = "重启"

    def generate_activities(self, agent_manager: AgentManager):
        activities = [
            agent_manager.restart(),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING, name=_("查询Proxy状态")),
        ]

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class InstallProxy(AgentAction):
    """
    安装Proxy，与安装Agent流程一致
    """

    ACTION_NAME = "INSTALL_PROXY"
    ACTION_DESCRIPTION = "安装"

    def generate_activities(self, agent_manager: AgentManager):
        register_host = agent_manager.register_host()
        if agent_manager.host_info["is_manual"]:
            self.ACTION_DESCRIPTION = "手动安装"
            install_name = _("手动安装")
        else:
            install_name = _("安装")

        activities = [
            register_host,
            agent_manager.query_tjj_password() if settings.USE_TJJ else None,
            agent_manager.configure_sy_policy() if settings.BKAPP_RUN_ENV == "shangyun" else None,
            agent_manager.configure_policy() if settings.BKAPP_RUN_ENV == "chuhai" else None,
            agent_manager.choose_ap(),
            agent_manager.install(install_name),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING, name=_("查询Proxy状态")),
        ]

        for file in FILES_TO_PUSH_TO_PROXY:
            activities.append(agent_manager.push_files_to_proxy(file["files"], name=file["name"]))
        activities.append(agent_manager.start_nginx())

        # 把注册 CMDB 得到的bk_host_id 作为输出给到后续节点使用
        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = NodeOutput(
            source_act=register_host.id, source_key="bk_host_id", type=Var.SPLICE, value="",
        )
        pipeline_data.inputs["${is_manual}"] = NodeOutput(
            source_act=register_host.id, source_key="is_manual", type=Var.SPLICE, value=False,
        )

        for plugin in self.step.auto_launch_plugins:
            activities.append(agent_manager.delegate_plugin(plugin.name))

        return activities, pipeline_data


class ReinstallProxy(AgentAction):
    """
    重装Proxy
    """

    ACTION_NAME = "REINSTALL_PROXY"
    ACTION_DESCRIPTION = "重装"

    def generate_activities(self, agent_manager: AgentManager):

        is_manual = Host.objects.get(bk_host_id=agent_manager.host_info["bk_host_id"]).is_manual
        if is_manual:
            install_name = _("手动安装")
        else:
            install_name = _("安装")

        activities = [
            agent_manager.query_tjj_password() if settings.USE_TJJ else None,
            agent_manager.configure_sy_policy() if settings.BKAPP_RUN_ENV == "shangyun" else None,
            agent_manager.configure_policy() if settings.BKAPP_RUN_ENV == "chuhai" else None,
            agent_manager.choose_ap(),
            agent_manager.install(install_name),
            agent_manager.wait(30),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING, name=_("查询Proxy状态")),
        ]

        for plugin in self.step.auto_launch_plugins:
            activities.append(agent_manager.delegate_plugin(plugin.name))

        # 推送文件到proxy
        for file in FILES_TO_PUSH_TO_PROXY:
            activities.append(agent_manager.push_files_to_proxy(file["files"], name=file["name"]))
        activities.append(agent_manager.start_nginx())

        pipeline_data = Data()
        is_manual = Host.objects.get(bk_host_id=agent_manager.host_info["bk_host_id"]).is_manual
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])
        pipeline_data.inputs["${is_manual}"] = Var(type=Var.PLAIN, value=is_manual)

        return activities, pipeline_data


class UpgradeProxy(ReinstallProxy):
    """
    升级Proxy
    """

    ACTION_NAME = "UPGRADE_PROXY"
    ACTION_DESCRIPTION = "升级"

    def generate_activities(self, agent_manager: AgentManager):
        push_upgrade_package = agent_manager.push_upgrade_package()
        activities = [
            push_upgrade_package,
            agent_manager.run_upgrade_command(),
            agent_manager.wait(30),
            agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING),
        ]

        # 推送文件到proxy
        for file in FILES_TO_PUSH_TO_PROXY:
            activities.append(agent_manager.push_files_to_proxy(file["files"], name=file["name"]))
        activities.append(agent_manager.start_nginx())

        pipeline_data = Data()
        pipeline_data.inputs["${package_name}"] = NodeOutput(
            source_act=push_upgrade_package.id, source_key="package_name", type=Var.SPLICE, value="",
        )
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class ReplaceProxy(InstallProxy):
    """
    替换Proxy
    """

    ACTION_NAME = "REPLACE_PROXY"
    ACTION_DESCRIPTION = "替换"


class UninstallAgent(AgentAction):
    """
    卸载Agent
    """

    ACTION_NAME = "UNINSTALL_AGENT"
    ACTION_DESCRIPTION = "卸载"

    def generate_activities(self, agent_manager: AgentManager):
        activities = [
            agent_manager.query_tjj_password() if settings.USE_TJJ else None,
            agent_manager.uninstall_agent(),
            agent_manager.get_agent_status(expect_status=ProcStateType.UNKNOWN),
            agent_manager.update_process_status(status=ProcStateType.NOT_INSTALLED),
        ]

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class UninstallProxy(AgentAction):
    """
    卸载Proxy
    """

    ACTION_NAME = "UNINSTALL_PROXY"
    ACTION_DESCRIPTION = "卸载"

    def generate_activities(self, agent_manager: AgentManager):
        activities = [
            agent_manager.uninstall_proxy(),
            agent_manager.get_agent_status(expect_status=ProcStateType.UNKNOWN, name=_("查询Proxy状态")),
            agent_manager.update_process_status(status=ProcStateType.NOT_INSTALLED),
        ]

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class ReloadAgent(AgentAction):
    """
    重载Agent
    """

    ACTION_NAME = "RELOAD_AGENT"
    ACTION_DESCRIPTION = "重载配置"

    def generate_activities(self, agent_manager: AgentManager):
        activities = [
            agent_manager.check_agent_status(),
            agent_manager.render_and_push_gse_config(),
        ]

        os_type = constants.OS_TYPE.get(agent_manager.host_info.get("bk_os_type"))
        if os_type != constants.OsType.WINDOWS:
            activities.append(agent_manager.reload_agent())
        else:
            activities.append(agent_manager.restart()),
            activities.append(agent_manager.get_agent_status(expect_status=ProcStateType.RUNNING)),

        pipeline_data = Data()
        pipeline_data.inputs["${bk_host_id}"] = Var(type=Var.PLAIN, value=agent_manager.host_info["bk_host_id"])

        return activities, pipeline_data


class ReloadProxy(ReloadAgent):
    """
    重载proxy
    """

    ACTION_NAME = "RELOAD_PROXY"
    ACTION_DESCRIPTION = "重载配置"
