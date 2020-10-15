# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import ntpath
import os
import posixpath

from django.conf import settings
from django.utils.translation import ugettext as _
from six.moves import range

from apps.backend.api.constants import ACCOUNT_MAP, OS, SUFFIX_MAP
from apps.backend.components.collections.gse import (
    GseDelegateProcessComponent,
    GseReloadProcessComponent,
    GseRestartProcessComponent,
    GseStartProcessComponent,
    GseStopProcessComponent,
    GseUnDelegateProcessComponent,
)
from apps.backend.components.collections.job import (
    JobAllocatePortComponent,
    JobFastExecuteScriptComponent,
    JobFastPushFileComponent,
    JobPushMultipleConfigFileComponent,
)
from apps.backend.components.collections.plugin import (
    ResetRetryTimesComponent,
    CheckAgentStatusComponent,
    RenderAndPushConfigComponent,
    UpdateHostProcessStatusComponent,
)
from apps.backend.plugin.tasks import run_pipeline, stop_pipeline
from apps.backend.utils.pipeline_parser import PipelineParser as CustomPipelineParser
from apps.backend.utils.pipeline_parser import parse_pipeline
from apps.node_man import constants
from apps.node_man.constants import OsType
from apps.node_man.models import Host, PipelineTree
from pipeline.builder import EmptyEndEvent, EmptyStartEvent, ServiceActivity, Var, build_tree
from pipeline.parser import PipelineParser

logger = logging.getLogger("app")


class CategoryType(object):
    official = "official"
    external = "external"


class StatusType(object):
    QUEUE = "QUEUE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


TARGET_PATH_MAP = {
    OS.LINUX: "/tmp/nodeman_upload/",
    OS.WINDOWS: "c:\\tmp\\nodeman_upload",
}

SCRIPT_TIMEOUT = 3000


class PluginManager(object):
    """
    插件动作管理
    """

    class ProcessStatus(object):
        UNKNOWN = "UNKNOWN"
        RUNNING = "RUNNING"
        TERMINATED = "TERMINATED"
        REMOVED = "REMOVED"

    def __init__(
        self, host_status, username, package=None, plugin=None, control=None, context=None,
    ):
        """
        :param HostStatus host_status: 主机插件信息
        :param username: 操作人
        """
        self.host_status = host_status
        self.host = Host.objects.get(bk_host_id=host_status.bk_host_id)

        # 路径处理器
        if self.host.os_type == OsType.WINDOWS:
            self.path_handler = ntpath
        else:
            self.path_handler = posixpath

        self.username = username

        # 目标主机IP，云区域信息
        self.host_info = host_status.host_info
        self.host_info["bk_cloud_id"] = int(self.host_info["bk_cloud_id"])
        self.host_info["bk_supplier_id"] = int(self.host_info["bk_supplier_id"])
        # 插件包信息
        self.package = package or host_status.package

        # 插件元信息
        self.plugin = plugin or self.package.plugin_desc

        # 插件控制信息，注意：优先使用 host_status 的控制信息
        self.control = control or self.package.proc_control

        # 初始化 API Client
        self.job_client = dict(bk_biz_id=self.host.bk_biz_id, username=self.username, os_type=self.package.os,)
        self.gse_client = dict(username=self.username, os_type=self.package.os)
        self.context = context

    def deploy(self):
        """
        下发插件包
        :return: pipeline活动节点 type: ServiceActivity
        """
        source_file = os.path.join(
            settings.NGINX_DOWNLOAD_PATH, self.package.os, self.package.cpu_arch, self.package.pkg_name,
        )
        source_ip_list = [dict(ip=settings.BKAPP_LAN_IP, bk_cloud_id=constants.DEFAULT_CLOUD)]
        file_target_path = TARGET_PATH_MAP.get(self.package.os, "/tmp/nodeman_upload/")
        file_source = [
            {"files": [source_file], "account": ACCOUNT_MAP.get(self.package.os, "root"), "ip_list": source_ip_list}
        ]
        act = ServiceActivity(component_code=JobFastPushFileComponent.code, name=_("下发插件包"))
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.file_target_path = Var(type=Var.PLAIN, value=file_target_path)
        act.component.inputs.file_source = Var(type=Var.PLAIN, value=file_source)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def install(self, keep_config=False, upgrade_type="OVERRIDE"):
        """
        安装插件
        """
        target_path = TARGET_PATH_MAP.get(self.package.os, "/tmp/nodeman_upload/")
        script_param = (
            "-t {category} -p {gse_home} -n {name} -f {package} -z {target} "
            "-m {upgrade_type} -d {tmp_dir}".format(
                category=self.plugin.category,
                gse_home=self.control.install_path,
                name=self.plugin.name,
                package=self.package.pkg_name,
                upgrade_type=upgrade_type,
                target=target_path,
                tmp_dir=self.host.agent_config["temp_path"],
            )
        )
        group_id = self.host_status.group_id
        os_type = self.package.os
        script_file = "update_binary.{}".format(SUFFIX_MAP[os_type])
        if self.plugin.category == CategoryType.external and group_id:
            # 设置插件实例目录
            script_param += " -i %s" % group_id
        if keep_config:
            script_param += " -u"
        path = os.path.join(os.path.dirname(__file__), "scripts", script_file)
        with open(path, encoding="utf-8") as fh:
            script_content = fh.read()

        act = ServiceActivity(component_code=JobFastExecuteScriptComponent.code, name=_("安装插件包"))
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        act.component.inputs.script_param = Var(type=Var.PLAIN, value=script_param)
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def uninstall(self):
        """
        卸载插件
        """
        script_param = "-t {category} -p {gse_home} -d {tmp_dir} -n {name} -r".format(
            category=self.plugin.category,
            gse_home=self.control.install_path,
            name=self.plugin.name,
            tmp_dir=self.host.agent_config["temp_path"],
        )
        group_id = self.host_status.group_id
        os_type = self.package.os
        script_file = "update_binary.{}".format(SUFFIX_MAP[os_type])
        if self.plugin.category == CategoryType.external and group_id:
            # 设置插件实例目录
            script_param += " -i %s" % group_id
        path = os.path.join(os.path.dirname(__file__), "scripts", script_file)
        with open(path, encoding="utf-8") as fh:
            script_content = fh.read()
        act = ServiceActivity(component_code=JobFastExecuteScriptComponent.code, name=_("卸载插件包"), error_ignorable=True)
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        act.component.inputs.script_param = Var(type=Var.PLAIN, value=script_param)
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def push_config(self):
        """
        下发配置
        """
        configs = self.host_status.configs
        install_path = self.control.install_path
        group_id = self.host_status.group_id

        plugin_root_mapping = {
            CategoryType.official: self.path_handler.join(install_path, "plugins"),
            CategoryType.external: self.path_handler.join(install_path, "external_plugins", group_id, self.plugin.name),
        }
        plugin_root = plugin_root_mapping[self.plugin.category]
        file_params = [
            {
                "file_target_path": self.path_handler.join(plugin_root, config["file_path"]),
                "file_list": [{"name": config["name"], "content": config["content"]}],
            }
            for config in configs
        ]
        act = ServiceActivity(component_code=JobPushMultipleConfigFileComponent.code, name=_("下发配置"))
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.file_params = Var(type=Var.PLAIN, value=file_params)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def remove_config(self):
        """
        移除配置
        """
        configs = self.host_status.configs
        install_path = self.control.install_path
        group_id = self.host_status.group_id
        os_type = self.package.os

        plugin_root_mapping = {
            CategoryType.official: self.path_handler.join(install_path, "plugins"),
            CategoryType.external: self.path_handler.join(install_path, "external_plugins", group_id, self.plugin.name),
        }
        plugin_root = plugin_root_mapping[self.plugin.category]
        config_path_list = [
            self.path_handler.join(plugin_root, config["file_path"], config["name"]) for config in configs
        ]
        script_file = "remove_config.{}".format(SUFFIX_MAP[os_type])
        if os_type == OS.WINDOWS:
            config_path_list = [self.path_handler.normpath(path.replace("/", "\\")) for path in config_path_list]
        else:
            config_path_list = [self.path_handler.normpath(path.replace("\\", "/")) for path in config_path_list]
        with open(os.path.join(os.path.dirname(__file__), "scripts", script_file), encoding="utf-8") as fh:
            script_content = fh.read()
        script_param = " ".join(config_path_list)
        act = ServiceActivity(component_code=JobFastExecuteScriptComponent.code, name=_("移除配置"), error_ignorable=True)
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        act.component.inputs.script_param = Var(type=Var.PLAIN, value=script_param)
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def allocate_port(self, listen_ip="127.0.0.1", port_range=""):
        """
        分配可用端口
        """
        if not port_range:
            port_range = self.control.port_range
        act = ServiceActivity(component_code=JobAllocatePortComponent.code, name=_("分配可用端口"))
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.host_status_id = Var(type=Var.PLAIN, value=self.host_status.id)
        act.component.inputs.listen_ip = Var(type=Var.PLAIN, value=listen_ip)
        act.component.inputs.port_range = Var(type=Var.PLAIN, value=port_range)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def _operate_process(self, component_code, act_name, error_ignorable=False):
        control = {
            "start_cmd": self.control.start_cmd,
            "stop_cmd": self.control.stop_cmd,
            "restart_cmd": self.control.restart_cmd,
            "reload_cmd": self.control.reload_cmd or self.control.restart_cmd,
            "kill_cmd": self.control.kill_cmd,
            "version_cmd": self.control.version_cmd,
            "health_cmd": self.control.health_cmd,
        }

        if self.plugin.category == CategoryType.external and self.host_status.group_id:
            proc_name = "{}_{}".format(self.host_status.group_id, self.plugin.name)
        else:
            proc_name = self.plugin.name

        act = ServiceActivity(component_code=component_code, name=act_name, error_ignorable=error_ignorable)
        act.component.inputs.gse_client = Var(type=Var.PLAIN, value=self.gse_client)
        act.component.inputs.hosts = Var(type=Var.PLAIN, value=[self.host_info])
        act.component.inputs.control = Var(type=Var.PLAIN, value=control)
        act.component.inputs.setup_path = Var(type=Var.PLAIN, value=self.host_status.setup_path)
        act.component.inputs.pid_path = Var(type=Var.PLAIN, value=self.host_status.pid_path)
        act.component.inputs.proc_name = Var(type=Var.PLAIN, value=proc_name)
        act.component.inputs.exe_name = Var(type=Var.PLAIN, value=self.control.process_name or self.plugin.name)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def start(self, error_ignorable=False):
        """
        启动插件
        """
        return self._operate_process(
            GseStartProcessComponent.code,
            _("启动 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def stop(self, error_ignorable=False):
        """
        停用插件
        """
        return self._operate_process(
            GseStopProcessComponent.code,
            _("停止 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def restart(self, error_ignorable=False):
        """
        重启插件
        """
        return self._operate_process(
            GseRestartProcessComponent.code,
            _("重启 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def reload(self, error_ignorable=False):
        """
        重启插件
        """
        return self._operate_process(
            GseReloadProcessComponent.code,
            _("重载 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def delegate(self, error_ignorable=False):
        """
        托管插件
        """
        return self._operate_process(
            GseDelegateProcessComponent.code,
            _("托管 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def undelegate(self, error_ignorable=False):
        """
        取消托管插件
        """
        return self._operate_process(
            GseUnDelegateProcessComponent.code,
            _("取消托管 {plugin_name} 插件进程").format(plugin_name=self.plugin.name),
            error_ignorable,
        )

    def debug(self, install_path, script_timeout=SCRIPT_TIMEOUT):
        """
        调试插件
        """
        # 临时替换安装路径，由于上层业务场景有限，这里暂未虑线程安全
        true_install_path = self.control.install_path
        self.control.install_path = install_path
        command = self.control.debug_cmd
        script_param = "-t {category} -p {install_path} -n {name} -c {command}".format(
            category=self.plugin.category, install_path=install_path, name=self.plugin.name, command=command,
        )

        script_file = "operate_plugin.{}".format(SUFFIX_MAP[self.package.os])
        path = os.path.join(os.path.dirname(__file__), "scripts", script_file)
        with open(path, encoding="utf-8") as fh:
            script_content = fh.read()

        debug = ServiceActivity(
            component_code=JobFastExecuteScriptComponent.code, name=_("开始调试插件"), error_ignorable=True,
        )
        debug.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        debug.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        debug.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        debug.component.inputs.script_param = Var(type=Var.PLAIN, value=script_param)
        debug.component.inputs.script_timeout = Var(type=Var.PLAIN, value=script_timeout)

        script_file = "stop_debug.{}".format(SUFFIX_MAP[self.package.os])
        script_param = "{} {}".format(install_path, self.plugin.name)
        path = os.path.join(os.path.dirname(__file__), "scripts", script_file)
        with open(path, encoding="utf-8") as fh:
            script_content = fh.read()

        stop_debug = ServiceActivity(component_code=JobFastExecuteScriptComponent.code, name=_("停止调试插件"))
        stop_debug.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        stop_debug.component.inputs.ip_list = Var(type=Var.PLAIN, value=[self.host_info])
        stop_debug.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        stop_debug.component.inputs.script_param = Var(type=Var.PLAIN, value=script_param)
        stop_debug.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        start.extend(self.deploy()).extend(self.install()).extend(self.push_config()).extend(debug).extend(
            stop_debug
        ).extend(self.set_process_status(self.ProcessStatus.REMOVED)).extend(end)
        tree = build_tree(start, replace_id=True)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        PipelineTree.objects.create(id=pipeline.id, tree=tree)
        run_pipeline.delay(pipeline)
        self.control.install_path = true_install_path
        return pipeline.id

    @staticmethod
    def get_debug_status(pipeline):
        def get_log_by_task_result(task_result):
            log = list()
            for res in task_result["failed"] + task_result["success"] + task_result["pending"]:
                log.append(res["log_content"])
            return "\n".join(log)

        def step_format_string(msg):
            """
            步骤分割符
            """
            return "\n************ %s ************\n" % msg

        tree_data = parse_pipeline(pipeline.tree)
        sorted_tree_data = sorted(list(tree_data.keys()), key=lambda key: tree_data[key]["index"])
        deploy, install, push_config, debug, stop_debug = (sorted_tree_data[i] for i in range(5))
        log_content = list()

        pipeline_parser = CustomPipelineParser([pipeline.id])

        steps = [
            (deploy, "DEPLOY_PLUGIN", _("下发插件包")),
            (install, "INSTALL_PLUGIN", _("安装插件包")),
            (push_config, "PUSH_CONFIG", _("下发配置文件")),
            (debug, "DEBUG_PROCESS", _("执行插件调试进程")),
            (stop_debug, "STOP_DEBUG_PROCESS", _("结束调试并回收资源")),
        ]

        for node_id, step_name, step_desc in steps:
            log_content.append(step_format_string("{} -【正在执行】".format(step_desc)))
            node_state = pipeline_parser.get_node_state(node_id)["status"]
            node_data = pipeline_parser.get_node_data(node_id)

            if node_state == "PENDING":
                return log_content, StatusType.RUNNING, step_name

            task_result = node_data["outputs"]
            if task_result and "task_result" in task_result:
                log_content.append(get_log_by_task_result(task_result["task_result"]))

            if node_state == "RUNNING":
                return log_content, StatusType.RUNNING, step_name

            if node_state == "FAILED" or node_data["ex_data"]:
                log_content.append(step_format_string("{} -【执行失败】".format(step_desc)))
                log_content.append("失败原因：{}".format(node_data["ex_data"]))
                return log_content, StatusType.FAILED, step_name

            log_content.append(step_format_string("{} -【执行成功】".format(step_desc)))

        return log_content, StatusType.SUCCESS, "STOP_DEBUG_PROCESS"

    @staticmethod
    def stop_debug(pipeline):
        tree_data = parse_pipeline(pipeline.tree)
        sorted_tree_data = sorted(list(tree_data.keys()), key=lambda key: tree_data[key]["index"])
        deploy, install, push_config, debug, stop_debug = (sorted_tree_data[i] for i in range(5))

        result = True
        message = "success"
        stop_pipeline.delay(pipeline.id, debug)
        # 其他情况不做任何操作
        return result, message

    def set_process_status(self, status):
        """
        设置插件状态
        """
        act = ServiceActivity(component_code=UpdateHostProcessStatusComponent.code, name=_("更新插件部署状态"))
        act.component.inputs.host_status_id = Var(type=Var.PLAIN, value=self.host_status.id)
        act.component.inputs.status = Var(type=Var.PLAIN, value=status)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def check_agent_status(self):
        """
        查询Agent状态是否正常
        """
        act = ServiceActivity(component_code=CheckAgentStatusComponent.code, name=_("查询Agent状态"))
        act.component.inputs.bk_host_id = Var(type=Var.PLAIN, value=self.host.bk_host_id)
        return act

    def render_and_push_config_by_subscription(self, subscription_step, instance_info, config_instances):
        """
        根据订阅配置生成并下发插件配置
        :param subscription_step: 订阅步骤
        :param instance_info:
        :param config_instances:
        :return:
        """
        config_instance_ids = [instance.id for instance in config_instances]
        act = ServiceActivity(component_code=RenderAndPushConfigComponent.code, name=_("渲染并下发配置"))
        act.component.inputs.subscription_step_id = Var(type=Var.PLAIN, value=subscription_step.id)
        act.component.inputs.instance_info = Var(type=Var.PLAIN, value=instance_info)
        act.component.inputs.host_status_id = Var(type=Var.PLAIN, value=self.host_status.id)
        act.component.inputs.config_instance_ids = Var(type=Var.PLAIN, value=config_instance_ids)
        act.component.inputs.job_client = Var(type=Var.PLAIN, value=self.job_client)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act

    def reset_retry_times(self):
        """
        重置重试次数
        """
        act = ServiceActivity(component_code=ResetRetryTimesComponent.code, name=_("重置重试次数"))
        act.component.inputs.host_status_id = Var(type=Var.PLAIN, value=self.host_status.id)
        act.component.inputs.context = Var(type=Var.PLAIN, value=self.context)
        return act
