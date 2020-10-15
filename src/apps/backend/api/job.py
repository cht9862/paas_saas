# -*- coding: utf-8 -*-


import base64
import logging
import time

import ujson as json
from django.conf import settings

from blueapps.utils.esbclient import get_client_by_user

from .constants import ACCOUNT_MAP, POLLING_INTERVAL, POLLING_TIMEOUT, SCRIPT_TYPE_MAP, JobIPStatus, ScriptType
from .errors import EmptyResponseError, FalseResultError, JobPollTimeout

logger = logging.getLogger("app")


class JobClient(object):
    """
    JOB客户端封装类
    """

    def __init__(self, bk_biz_id, username, os_type, **kwargs):
        """
        基本参数配置
        :param bk_biz_id: 业务id
        :param username: 用户名
        :param ip_list: 目标机器
               example: [
                   {
                       'ip': '10.0.1.10',
                       'bk_supplier_id': 0,
                       'bk_cloud_id': 0
                   }
               ]
        :param os_type: example: OS.LINUX
        """
        self.bk_biz_id = settings.BLUEKING_BIZ_ID if settings.JOB_VERSION == "V3" else bk_biz_id
        self.username = settings.BACKEND_JOB_OPERATOR if settings.JOB_VERSION == "V3" else username
        self.os_type = os_type
        self.client = get_client_by_user(settings.BACKEND_JOB_OPERATOR)
        self.account = ACCOUNT_MAP.get(os_type, "root")

    def _response_exception_filter(self, api_name, params, response):
        """
        响应异常过滤器
        :param api_name: example: client.gse.register_proc_info
        :param params: api参数
        :param response: 响应
        :return: response['result']
        """
        if not response:
            logger.error(
                "user->[{}] called JOB api->[{}] with params->[{}] but got no response.".format(
                    self.username, api_name, json.dumps(params)
                )
            )
            raise EmptyResponseError({"api_name": api_name})
        if not response["result"]:
            logger.error(
                logger.error(
                    "user->[{}] called JOB api->[{}] with params->[{}] but an error->[FalseResultError] occurred."
                    "Full response->[{}].".format(self.username, params, api_name, json.dumps(response))
                )
            )
            raise FalseResultError({"api_name": api_name, "error_message": response["message"]})
        return response["data"]

    def get_task_result(self, job_instance_id):
        """
        获取执行结果
        :param job_instance_id: job任务id
        :return: example: {
                    "success": [
                        {
                            'ip': 10.0.0.1,
                            'bk_cloud_id': 0,
                            'log_content': 'xx',
                            'error_code': 0,
                            'exit_code': 0
                        }
                    ],
                    "pending": [],
                    "failed": []
                }
        """
        params = {
            "job_instance_id": job_instance_id,
            "bk_biz_id": self.bk_biz_id,
            "bk_username": self.username,
        }
        response = self.client.job.get_job_instance_log(**params)
        logger.info(
            "user->[{}] called api->[{}] and got response->[{}].".format(
                self.username, job_instance_id, json.dumps(response)
            )
        )
        data = self._response_exception_filter("client.job.get_job_instance_log", params, response)
        is_finished = data[0]["is_finished"]
        task_result = {
            "success": [],
            "pending": [],
            "failed": [],
        }
        for step_result in data[0].get("step_results", []):
            if step_result["ip_status"] == JobIPStatus.SUCCESS:
                key = "success"
            elif step_result["ip_status"] in (JobIPStatus.WAITING_FOR_EXEC, JobIPStatus.RUNNING,):
                key = "pending"
            else:
                key = "failed"
            for ip_log in step_result.get("ip_logs", []):
                task_result[key].append(
                    {
                        "ip": ip_log["ip"],
                        "bk_cloud_id": ip_log["bk_cloud_id"],
                        "log_content": ip_log["log_content"],
                        "error_code": ip_log["error_code"],
                        "exit_code": ip_log["exit_code"],
                    }
                )

        return is_finished, task_result

    def poll_task_result(self, job_instance_id):
        """
        轮询直到任务完成
        :param job_instance_id: job任务id
        :return: 与 get_task_result 同
        """
        polling_time = 0
        is_finished, task_result = self.get_task_result(job_instance_id)
        while not is_finished:
            if polling_time > POLLING_TIMEOUT:
                logger.error(
                    "user->[{}] called api->[get_task_result] but got JobExecuteTimeout.".format(self.username)
                )
                raise JobPollTimeout({"job_instance_id": job_instance_id})

            # 每次查询后，睡觉
            polling_time += POLLING_INTERVAL
            time.sleep(POLLING_INTERVAL)

            is_finished, task_result = self.get_task_result(job_instance_id)

        return is_finished, task_result

    def push_config_file(self, ip_list, file_target_path, file_list):
        """
        上传配置文件
        :param ip_list: 目标机器
               example: [
                   {
                       'ip': '10.0.1.10',
                       'bk_supplier_id': 0,
                       'bk_cloud_id': 0
                   }
               ]
        :param file_target_path: 目标路径
               example: '/data/'
        :param file_list: 文件
               example: [
                   {
                       'name': 'test',
                       'content': 'xx'
                   }
               ]
        :return: Job任务id
        """
        file_list = [
            {"file_name": single_file["name"], "content": base64.b64encode(single_file["content"].encode()).decode()}
            for single_file in file_list
        ]
        params = {
            "bk_username": self.username,
            "bk_biz_id": self.bk_biz_id,
            "account": self.account,
            "file_target_path": file_target_path,
            "file_list": file_list,
            "ip_list": ip_list,
        }
        response = self.client.job.push_config_file(params)
        data = self._response_exception_filter("client.job.push_config_file", params, response)
        return data["job_instance_id"]

    def fast_execute_script(self, ip_list, script_content, script_param, script_timeout=3000):
        """
        快速执行脚本
        :param ip_list: 目标机器
               example: [
                   {
                       'ip': '10.0.1.10',
                       'bk_supplier_id': 0,
                       'bk_cloud_id': 0
                   }
               ]
        :param script_content: example: 'ls'
        :param script_param: example: './'
        :param script_timeout: example: 3000
        :return: Job任务id
        """
        # @TODO execute_platform_job 从上云环境开始下架
        if settings.JOB_VERSION == "V2":
            params = {
                "bk_username": self.username,
                "source_bk_biz_id": 2,
                "target_bk_biz_id": self.bk_biz_id,
                "bk_job_id": 7,
                "steps": [
                    {
                        "script_timeout": script_timeout,
                        "ip_list": ip_list,
                        "script_param": base64.b64encode(script_param.encode()).decode(),
                        "script_content": base64.b64encode(script_content.encode()).decode(),
                        "step_id": 19,
                        "account": self.account,
                        "script_type": SCRIPT_TYPE_MAP.get(self.os_type, ScriptType.SHELL),
                    }
                ],
            }
            response = self.client.job.execute_platform_job(params)
            data = self._response_exception_filter("client.job.execute_platform_job", params, response)
        else:
            params = {
                "bk_biz_id": settings.BLUEKING_BIZ_ID,
                "script_content": base64.b64encode(script_content.encode()).decode(),
                "script_param": base64.b64encode(script_param.encode()).decode(),
                "script_timeout": script_timeout,
                "account": self.account,
                "script_type": SCRIPT_TYPE_MAP.get(self.os_type, ScriptType.SHELL),
                "ip_list": ip_list,
            }
            response = self.client.job.fast_execute_script(params)
            data = self._response_exception_filter("client.job.fast_execute_script", params, response)
        return data["job_instance_id"]

    def fast_push_file(self, ip_list, file_target_path, file_source):
        """
        快速分发文件
        :param ip_list: 目标机器
               example: [
                   {
                       'ip': '10.0.1.10',
                       'bk_supplier_id': 0,
                       'bk_cloud_id': 0
                   }
               ]
        :param file_target_path: example: '/data/'
        :param file_source: example: [
                                {
                                    "files": [
                                        "/data/dev_pipeline_unit_test"
                                    ],
                                    "account": "root",
                                    "ip_list": [
                                        {
                                            "bk_cloud_id": 0,
                                            "ip": "10.0.1.10",
                                            'bk_supplier_id': 0
                                        }
                                    ]
                                }
                            ]
        :return: Job任务id
        """
        # @TODO execute_platform_job 从上云环境开始下架
        if settings.JOB_VERSION == "V2":
            params = {
                "bk_username": self.username,
                "source_bk_biz_id": 2,
                "target_bk_biz_id": self.bk_biz_id,
                "bk_job_id": 7,
                "steps": [
                    {
                        "file_target_path": file_target_path,
                        "file_source": file_source,
                        "ip_list": ip_list,
                        "step_id": 20,
                        "account": self.account,
                    }
                ],
            }
            response = self.client.job.execute_platform_job(params)
            data = self._response_exception_filter("client.job.execute_platform_job", params, response)
        else:
            params = {
                "bk_biz_id": settings.BLUEKING_BIZ_ID,
                "file_target_path": file_target_path,
                "file_source": file_source,
                "ip_list": ip_list,
                "account": self.account,
                "bk_username": self.username,
            }
            response = self.client.job.fast_push_file(params)
            data = self._response_exception_filter("client.job.fast_push_file", params, response)

        return data["job_instance_id"]


class DummyJobClient(JobClient):
    """
    dummy job client
    """

    TASK_RESULT = {
        "success": [{"ip": "10.0.1.10", "bk_cloud_id": 0, "log_content": "dummy-job-log-content"}],
        "pending": [],
        "failed": [],
    }

    def fast_push_file(self, ip_list, file_target_path, file_source):
        return "dummy-job-instance-id"

    def push_config_file(self, ip_list, file_target_path, file_list):
        return "dummy-job-instance-id"

    def fast_execute_script(self, ip_list, script_content, script_param, script_timeout=3000):
        return "dummy-job-instance-id"

    def get_task_result(self, job_instance_id):
        return True, self.TASK_RESULT


# JobClient = DummyJobClient
