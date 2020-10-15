# -*- coding: utf-8 -*-

import abc
import copy
import logging
import os
from collections import defaultdict

import six
import ujson as json
from django.db import IntegrityError
from six.moves import range

from apps.backend.api.constants import POLLING_INTERVAL, POLLING_TIMEOUT, SUFFIX_MAP
from apps.backend.api.job import JobClient
from apps.node_man.models import ProcControl, ProcessStatus
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service, StaticIntervalGenerator

logger = logging.getLogger("app")


class JobBaseService(six.with_metaclass(abc.ABCMeta, Service)):
    """
    JOB Service 基类
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

    def log_by_task_result(self, job_instance_id, task_result, log_context=None):
        for res in task_result.get("success", []):
            # self.log_info("JOB(task_id: [{}], ip: [{}]) get schedule finished with task result:\n[{}].".format(
            #     job_instance_id,
            #     res['ip'],
            #     res['log_content']),
            #     log_context
            # )
            self.log_info(
                "JOB(task_id: [{}], ip: [{}]) get schedule finished.".format(job_instance_id, res["ip"]), log_context,
            )
        for res in task_result.get("failed", []) + task_result.get("pending", []):
            self.log_error(
                "JOB(task_id: [{}], ip: [{}]) get schedule failed with task result:\n[{}].".format(
                    job_instance_id, res["ip"], res["log_content"]
                ),
                log_context,
            )

    @abc.abstractmethod
    def execute(self, data, parent_data):
        raise NotImplementedError()

    def schedule(self, data, parent_data, callback_data=None):
        job_instance_id = data.get_one_of_outputs("job_instance_id")
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        polling_time = data.get_one_of_outputs("polling_time")
        log_context = data.get_one_of_inputs("context")
        is_finished, task_result = job_client.get_task_result(job_instance_id)
        data.outputs.task_result = task_result
        self.log_debug(
            "JOB(task_id: [{}]) get schedule task result:\n[{}].".format(job_instance_id, json.dumps(task_result)),
            log_context,
        )
        if is_finished:
            self.log_by_task_result(job_instance_id, task_result, log_context)
            self.finish_schedule()
            if task_result["failed"]:
                data.outputs.ex_data = "以下主机JOB任务执行失败：{}".format(
                    ",".join([host["ip"] for host in task_result["failed"]])
                )
                return False
            else:
                return True
        elif polling_time + POLLING_INTERVAL > POLLING_TIMEOUT:
            self.log_error(
                "JOB(job_instance_id: [{}]) schedule timeout.".format(job_instance_id), log_context,
            )
            data.outputs.ex_data = "任务轮询超时"
            self.finish_schedule()
            return False

        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        return True


class JobPushConfigFileService(JobBaseService):
    """
    JOB Service 上传配置文件
    """

    def execute(self, data, parent_data):
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        ip_list = data.get_one_of_inputs("ip_list")
        file_target_path = data.get_one_of_inputs("file_target_path")
        file_list = data.get_one_of_inputs("file_list")
        log_context = data.get_one_of_inputs("context")
        self.log_info(
            "JobPushConfigFileService called with params:\n {}, {}, {}.".format(
                json.dumps(ip_list), file_target_path, json.dumps(file_list)
            ),
            log_context,
        )
        if not all(
            [isinstance(ip_list, list), isinstance(file_target_path, six.string_types), isinstance(file_list, list)]
        ):
            self.log_error("JobPushConfigFileService params checked failed.", log_context)
            data.outputs.ex_data = "参数校验失败"
            return False
        job_instance_id = job_client.push_config_file(ip_list, file_target_path, file_list)
        data.outputs.job_instance_id = job_instance_id
        data.outputs.polling_time = 0
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="list", required=True),
            Service.InputItem(name="file_target_path", key="file_target_path", type="str", required=True,),
            Service.InputItem(name="file_list", key="file_list", type="list", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="job_instance_id", key="job_instance_id", type="int"),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(name="task_result", key="task_result", type="dict"),
        ]


class JobFastExecuteScriptService(JobBaseService):
    """
    JOB Service 快速执行脚本
    """

    ACTION_NAME = "EXECUTE_SCRIPT"
    ACTION_DESCRIPTION = "执行脚本"

    def execute(self, data, parent_data):
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        ip_list = data.get_one_of_inputs("ip_list")
        script_timeout = data.get_one_of_inputs("script_timeout")
        script_content = data.get_one_of_inputs("script_content")
        script_param = data.get_one_of_inputs("script_param")
        log_context = data.get_one_of_inputs("context")
        self.log_info(
            "JobFastExecuteScriptService called for {} with script_params:\n {}.".format(
                json.dumps(ip_list), script_param
            ),
            log_context,
        )
        if not all(
            [
                isinstance(ip_list, list),
                isinstance(script_content, six.string_types),
                isinstance(script_timeout, int),
                isinstance(script_param, six.string_types),
            ]
        ):
            self.log_error("JobFastExecuteScriptService params checked failed.", log_context)
            data.outputs.ex_data = "参数校验失败"
            return False
        job_instance_id = job_client.fast_execute_script(ip_list, script_content, script_param, script_timeout)
        data.outputs.job_instance_id = job_instance_id
        data.outputs.polling_time = 0
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="list", required=True),
            Service.InputItem(name="script_content", key="script_content", type="str", required=True),
            Service.InputItem(name="script_param", key="script_param", type="str", required=True),
            Service.InputItem(name="script_timeout", key="script_timeout", type="int", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="job_instance_id", key="job_instance_id", type="int"),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(name="task_result", key="task_result", type="dict"),
        ]


class JobFastPushFileService(JobBaseService):
    """
    JOB Service 快速分发文件
    """

    ACTION_NAME = "PUSH_FILE"
    ACTION_DESCRIPTION = "分发文件"

    def execute(self, data, parent_data):
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        ip_list = data.get_one_of_inputs("ip_list")
        file_target_path = data.get_one_of_inputs("file_target_path")
        file_source = data.get_one_of_inputs("file_source")
        log_context = data.get_one_of_inputs("context")
        self.log_info(
            "JobFastPushFileService called with params:\n ip_list:{}, file_target_path:{}, file_source:{}.".format(
                json.dumps(ip_list, indent=2), file_target_path, json.dumps(file_source, indent=2),
            ),
            log_context,
        )
        if not all(
            [isinstance(ip_list, list), isinstance(file_target_path, six.string_types), isinstance(file_source, list)]
        ):
            self.log_error("JobFastPushFileService params checked failed.", log_context)
            data.outputs.ex_data = "参数校验失败"
            return False
        job_instance_id = job_client.fast_push_file(ip_list, file_target_path, file_source)
        data.outputs.job_instance_id = job_instance_id
        data.outputs.polling_time = 0
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="list", required=True),
            Service.InputItem(name="file_target_path", key="file_target_path", type="str", required=True,),
            Service.InputItem(name="file_source", key="file_source", type="list", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="job_instance_id", key="job_instance_id", type="int"),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(name="task_result", key="task_result", type="dict"),
        ]


class JobPushMultipleConfigFileService(JobBaseService):
    """
    JOB Service 上传多个配置文件
    """

    def schedule(self, data, parent_data, callback_data=None):
        unfinished_job_instance_ids = data.get_one_of_outputs("unfinished_job_instance_ids")
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        polling_time = data.get_one_of_outputs("polling_time")
        log_context = data.get_one_of_inputs("context")
        finished = set()
        for job_instance_id in unfinished_job_instance_ids:
            is_finished, task_result = job_client.get_task_result(job_instance_id)
            self.log_debug(
                "JOB(job_instance_id: [{}]) get task result: [{}].".format(job_instance_id, json.dumps(task_result)),
                log_context,
            )
            if is_finished:
                self.log_by_task_result(job_instance_id, task_result, log_context)
                finished.add(job_instance_id)
                old_task_result = data.get_one_of_outputs("task_result", defaultdict(list))
                for k in ("success", "failed", "pending"):
                    old_task_result[k].extend(task_result[k])
                data.outputs.task_result = old_task_result
        unfinished_job_instance_ids -= finished
        if not unfinished_job_instance_ids:
            self.finish_schedule()
            return True
        elif polling_time + POLLING_INTERVAL > POLLING_TIMEOUT:
            self.log_error(
                "JOB(job_instance_ids: [{}]) schedule timeout.".format(json.dumps(unfinished_job_instance_ids)),
                log_context,
            )
            data.outputs.ex_data = "任务轮询超时"
            return False
        data.outputs.unfinished_job_instance_ids = unfinished_job_instance_ids
        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        return True

    def execute(self, data, parent_data):
        job_client = JobClient(**data.get_one_of_inputs("job_client"))
        ip_list = data.get_one_of_inputs("ip_list")
        file_params = data.get_one_of_inputs("file_params")
        log_context = data.get_one_of_inputs("context")
        if not all([isinstance(ip_list, list), isinstance(file_params, list)]):
            self.log_error("JobPushMultipleConfigFileService params checked failed.", log_context)
            data.outputs.ex_data = "参数校验失败"
            return False
        self.log_info(
            "JobPushMultipleConfigFileService called with params:\n {}, {}.".format(
                json.dumps(ip_list), json.dumps(file_params)
            ),
            log_context,
        )
        job_instance_ids = set()
        for file_param in file_params:
            file_target_path = file_param.get("file_target_path")
            file_list = file_param.get("file_list")
            job_instance_id = job_client.push_config_file(ip_list, file_target_path, file_list)
            job_instance_ids.add(job_instance_id)
        data.outputs.job_instance_ids = job_instance_ids
        data.outputs.unfinished_job_instance_ids = copy.copy(job_instance_ids)
        data.outputs.polling_time = 0
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="list", required=True),
            Service.InputItem(name="file_params", key="file_params", type="str", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="job_instance_ids", key="job_instance_id", type="set"),
            Service.OutputItem(name="unfinished_job_instance_ids", key="unfinished_job_instance_ids", type="set",),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(name="task_result", key="task_result", type="dict"),
        ]


class JobAllocatePortService(JobFastExecuteScriptService):
    def execute(self, data, parent_data):
        host_status_id = data.get_one_of_inputs("host_status_id")
        host_status = ProcessStatus.objects.get(id=host_status_id)
        script_file = "fetch_used_ports.{}".format(SUFFIX_MAP[host_status.package.os])
        path = os.path.join(os.path.dirname(__file__), "../../plugin/scripts/", script_file)
        with open(path, encoding="utf-8") as fh:
            script_content = fh.read()
        host_info = host_status.host_info
        host_info["bk_cloud_id"] = int(host_info["bk_cloud_id"])
        host_info["bk_supplier_id"] = int(host_info["bk_supplier_id"])
        data.inputs.ip_list = [host_info]
        data.inputs.script_param = ""
        data.inputs.script_timeout = 3000
        data.inputs.script_content = script_content
        return super(JobAllocatePortService, self).execute(data, parent_data)

    def schedule(self, data, parent_data, callback_data=None):
        log_context = data.get_one_of_inputs("context")
        result = super(JobAllocatePortService, self).schedule(data, parent_data, callback_data)
        if not self.is_schedule_finished():
            # 如果轮询未结束，要么发生了错误，要么还需要继续轮询，因此直接返回result
            return result
        # 解析脚本中的端口列表
        used_ports = set()
        host_log = data.get_one_of_outputs("task_result")["success"][0]
        for line in host_log["log_content"].splitlines():
            try:
                if ":" in line:
                    port_num = int(line.split(":")[-1])
                else:
                    # AIX使用 "." 来分隔端口
                    port_num = int(line.split(".")[-1])
            except Exception:
                pass
            else:
                used_ports.add(port_num)
        port_range = data.get_one_of_inputs("port_range")
        host_status_id = data.get_one_of_inputs("host_status_id")
        host_status = ProcessStatus.objects.get(id=host_status_id)
        listen_ip = data.get_one_of_inputs("listen_ip")
        port_range_list = ProcControl.parse_port_range(port_range)
        queryset = ProcessStatus.objects.filter(bk_host_id=host_status.bk_host_id)
        # 当前主机已经注册的端口号集合
        registered_ports = {port for port in queryset.values_list("listen_port", flat=True) if port}
        registered_ports.update(used_ports)
        # 在给定范围内检索可用的端口号
        for port_min, port_max in port_range_list:
            for port in range(port_min, port_max + 1):
                if port not in registered_ports:
                    # 检索完成，保存退出
                    host_status.listen_ip = listen_ip
                    host_status.listen_port = port
                    try:
                        host_status.save()
                    except IntegrityError:
                        # 不满足完整性校验，端口冲突，需要继续检查
                        continue
                    data.outputs.listen_port = port
                    return True
        self.log_error("主机[{}]在ip->[{}]上无可用端口".format(host_log["ip"], listen_ip), log_context)
        data.outputs.ex_data = "主机[{}]在ip->[{}]上无可用端口".format(host_log["ip"], listen_ip)
        return False

    def inputs_format(self):
        return [
            Service.InputItem(name="job_client", key="job_client", type="dict", required=True),
            Service.InputItem(name="ip_list", key="ip_list", type="list", required=True),
            Service.InputItem(name="script_content", key="script_content", type="str", required=True),
            Service.InputItem(name="script_param", key="script_param", type="str", required=True),
            Service.InputItem(name="script_timeout", key="script_timeout", type="int", required=True),
            Service.InputItem(name="host_status_id", key="host_status_id", type="int", required=True),
            Service.InputItem(name="listen_ip", key="listen_ip", type="str", required=True),
            Service.InputItem(name="port_range", key="port_range", type="str", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="job_instance_id", key="job_instance_id", type="int"),
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(name="task_result", key="task_result", type="dict"),
            Service.OutputItem(name="listen_port", key="listen_port", type="int"),
        ]


class JobPushConfigFileComponent(Component):
    name = "JobPushConfigFileComponent"
    code = "job_push_config_file"
    bound_service = JobPushConfigFileService


class JobFastExecuteScriptComponent(Component):
    name = "JobFastExecuteScriptComponent"
    code = "job_fast_execute_script"
    bound_service = JobFastExecuteScriptService


class JobFastPushFileComponent(Component):
    name = "JobFastPushFileComponent"
    code = "job_fast_push_file"
    bound_service = JobFastPushFileService


class JobPushMultipleConfigFileComponent(Component):
    name = "JobPushMultipleConfigFileComponent"
    code = "job_push_multiple_config_file"
    bound_service = JobPushMultipleConfigFileService


class JobAllocatePortComponent(Component):
    name = "JobAllocatePortComponent"
    code = "job_allocate_port"
    bound_service = JobAllocatePortService
