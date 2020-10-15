# -*- coding: utf-8 -*-
import abc
import logging
import six

from apps.backend.api.constants import POLLING_INTERVAL, POLLING_TIMEOUT
from apps.backend.api.sops import SopsClient
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service, StaticIntervalGenerator

logger = logging.getLogger("app")


class SopsBaseService(six.with_metaclass(abc.ABCMeta, Service)):
    """
    SOPS Service 基类
    """

    __need_schedule__ = True
    interval = StaticIntervalGenerator(POLLING_INTERVAL)

    def _append_log_context(self, msg, log_context):
        prefix = ""
        if isinstance(log_context, dict):
            prefix = ", ".join("{}({})".format(key, value) for key, value in log_context.items())
            prefix += " "
        return prefix + msg

    def log_info(self, msg, log_context=None):
        logger.info(self._append_log_context(msg, log_context))
        self.logger.info(msg)

    def log_error(self, msg, log_context=None):
        logger.error(self._append_log_context(msg, log_context))
        self.logger.error(msg)

    def log_warning(self, msg, log_context=None):
        logger.warning(self._append_log_context(msg, log_context))
        self.logger.warning(msg)

    def log_debug(self, msg, log_context=None):
        logger.debug(self._append_log_context(msg, log_context))
        # self.logger.debug(msg)

    @abc.abstractmethod
    def execute(self, data, parent_data):
        raise NotImplementedError()

    def schedule(self, data, parent_data, callback_data=None):
        task_id = data.get_one_of_outputs("task_id")
        sops_client = SopsClient(**data.get_one_of_inputs("sops_client"))
        polling_time = data.get_one_of_outputs("polling_time")

        log_context = data.get_one_of_inputs("context")
        state = sops_client.get_task_status(task_id)
        self.log_debug(
            "SOPS(task_id: [{}]) get schedule task status:[{}].".format(task_id, state), log_context,
        )
        if state == "FINISHED":
            self.finish_schedule()
            return True

        elif polling_time + POLLING_INTERVAL > POLLING_TIMEOUT:
            self.log_error(
                "SOPS(task_id: [{}]) schedule timeout. status:[{}]".format(task_id, state), log_context,
            )
            data.outputs.ex_data = "任务轮询超时"
            self.finish_schedule()
            return False

        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        return True


class CreateAndStartTaskService(SopsBaseService):
    """
    创建并开始任务
    """

    def inputs_format(self):
        return [
            Service.InputItem(name="sops_client", key="sops_client", type="dict", required=True),
            Service.InputItem(name="template_id", key="template_id", type="int", required=True),
            Service.InputItem(name="name", key="name", type="str", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="str", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="task_id", key="task_id", type="int"),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
        ]

    def execute(self, data, parent_data):
        sops_client = SopsClient(**data.get_one_of_inputs("sops_client"))
        template_id = data.get_one_of_inputs("template_id")
        name = data.get_one_of_inputs("name")
        ip_list = data.get_one_of_inputs("ip_list")
        log_context = data.get_one_of_inputs("context")
        task_id = sops_client.create_task(name, template_id, ip_list)
        sops_client.start_task(task_id)
        self.log_info(
            "SOPS task id:[{}].".format(task_id), log_context,
        )
        data.outputs.task_id = task_id
        data.outputs.polling_time = 0
        return True


class CreateAndStartTaskComponent(Component):
    name = "CreateAndStartTaskComponent"
    code = "create_and_start_task"
    bound_service = CreateAndStartTaskService
