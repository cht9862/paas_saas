# -*- coding: utf-8 -*-
import ntpath
import posixpath

from django.utils.translation import ugettext as _

from apps.backend.components.collections.job import JobPushMultipleConfigFileService
from apps.backend.subscription.tools import get_all_subscription_steps_context, render_config_files
from apps.node_man import constants
from apps.node_man.constants import CategoryType, OsType
from apps.node_man.models import PluginConfigInstance, ProcessStatus, SubscriptionStep
from pipeline.component_framework.component import Component
from pipeline.core.flow import Service


class UpdateHostProcessStatusService(Service):
    """
    更新主机进程状态
    """

    def inputs_format(self):
        return [
            Service.InputItem(name="host_status_id", key="host_status_id", type="int", required=True),
            Service.InputItem(name="status", key="status", type="str", required=True),
        ]

    def execute(self, data, parent_data):
        host_status_id = data.get_one_of_inputs("host_status_id")
        status = data.get_one_of_inputs("status")
        if status not in ["RUNNING", "UNKNOWN", "TERMINATED", "REMOVED"]:
            data.outputs.ex_data = _("进程的目标状态不合法：{}").format(status)
            return False
        try:
            host_status = ProcessStatus.objects.get(id=host_status_id)
        except ProcessStatus.DoesNotExist:
            data.outputs.ex_data = _("进程状态记录不存在：{}").format(host_status_id)
            return False

        if status == "REMOVED":
            host_status.delete()
        else:
            host_status.status = status
            host_status.save()
        return True


class CheckAgentStatusService(Service):
    def inputs_format(self):
        return [
            Service.InputItem(name="bk_host_id", key="bk_host_id", type="int", required=True),
        ]

    def execute(self, data, parent_data):
        bk_host_id = data.get_one_of_inputs("bk_host_id")
        agent_status = ProcessStatus.objects.get(bk_host_id=bk_host_id, name=ProcessStatus.GSE_AGENT_PROCESS_NAME)
        if agent_status.status == constants.ProcStateType.RUNNING:
            self.logger.info(_("Agent 状态【正常】"))
            return True
        else:
            self.logger.error(_("Agent 状态【异常】"))
            return False


class RenderAndPushConfigService(JobPushMultipleConfigFileService):
    """
    获取订阅步骤上下文数据
    """

    def inputs_format(self):
        return [
            Service.InputItem(name="subscription_step_id", key="subscription_step_id", type="int", required=True,),
            Service.InputItem(name="instance_info", key="instance_info", type="dict", required=True),
            Service.InputItem(name="host_status_id", key="host_status_id", type="int", required=True),
            Service.InputItem(name="config_instance_ids", key="config_instance_ids", type="list", required=True,),
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
        ]

    def execute(self, data, parent_data):
        subscription_step_id = data.get_one_of_inputs("subscription_step_id")
        instance_info = data.get_one_of_inputs("instance_info")
        host_status_id = data.get_one_of_inputs("host_status_id")
        config_instance_ids = data.get_one_of_inputs("config_instance_ids")

        try:
            host_status = ProcessStatus.objects.get(id=host_status_id)
        except ProcessStatus.DoesNotExist:
            data.outputs.ex_data = _("进程状态记录不存在：{}").format(host_status_id)
            return False

        try:
            subscription_step = SubscriptionStep.objects.get(id=subscription_step_id)
        except SubscriptionStep.DoesNotExist:
            data.outputs.ex_data = _("订阅步骤记录不存在：{}").format(subscription_step_id)
            return False

        config_templates = PluginConfigInstance.objects.filter(id__in=config_instance_ids)

        context = get_all_subscription_steps_context(
            subscription_step, instance_info, host_status.host_info, host_status.name
        )
        rendered_configs = render_config_files(config_templates, host_status, context)

        host_status.configs = rendered_configs
        host_status.save()

        # 路径处理器
        if host_status.host.os_type == OsType.WINDOWS:
            path_handler = ntpath
        else:
            path_handler = posixpath

        plugin_root_mapping = {
            CategoryType.official: path_handler.dirname(host_status.setup_path),
            CategoryType.external: host_status.setup_path,
        }
        plugin_root = plugin_root_mapping[host_status.package.plugin_desc.category]
        file_params = [
            {
                "file_target_path": path_handler.join(plugin_root, config["file_path"]),
                "file_list": [{"name": config["name"], "content": config["content"]}],
            }
            for config in rendered_configs
        ]
        data.inputs.ip_list = [host_status.host_info]
        data.inputs.file_params = file_params

        return super(RenderAndPushConfigService, self).execute(data, parent_data)


class UpdateHostProcessStatusComponent(Component):
    name = "UpdateHostProcessStatus"
    code = "update_host_process_status"
    bound_service = UpdateHostProcessStatusService


class ResetRetryTimesService(Service):
    """
    重置重试次数
    """

    def inputs_format(self):
        return [
            Service.InputItem(name="host_status_id", key="host_status_id", type="int", required=True),
        ]

    def execute(self, data, parent_data):
        host_status_id = data.get_one_of_inputs("host_status_id")
        try:
            host_status = ProcessStatus.objects.get(id=host_status_id)
            # 成功执行到最后的更新状态步骤，把重试次数清零
            host_status.retry_times = 0
            host_status.save()
        except ProcessStatus.DoesNotExist:
            data.outputs.ex_data = _("进程状态记录不存在：{}，若是移除操作，请忽略此问题。").format(host_status_id)
            return True

        return True


class CheckAgentStatusComponent(Component):
    name = "CheckAgentStatus"
    code = "check_agent_status"
    bound_service = CheckAgentStatusService


class RenderAndPushConfigComponent(Component):
    name = "RenderAndPushConfig"
    code = "render_and_push_config"
    bound_service = RenderAndPushConfigService


class ResetRetryTimesComponent(Component):
    name = "ResetRetryTimes"
    code = "reset_retry_times"
    bound_service = ResetRetryTimesService
