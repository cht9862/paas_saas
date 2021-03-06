# -*- coding: utf-8 -*-
from mock import patch

from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)

from apps.backend.api.constants import OS
from apps.backend.components.collections.job import JobFastExecuteScriptComponent
from apps.backend.tests.components.collections.job import utils


class JobFastExecuteScriptComponentTestCase(TestCase, ComponentTestMixin):
    JOB_CLIENT = {"bk_biz_id": 2, "username": "admin", "os_type": OS.LINUX}

    TASK_RESULT = {
        "success": [{"ip": "20.8.3.1", "bk_cloud_id": 0, "log_content": "success", "error_code": 0, "exit_code": 0}],
        "pending": [],
        "failed": [],
    }

    JOB_FAST_EXECUTE_SCRIPT = {
        "job_client": JOB_CLIENT,
        "ip_list": [{"ip": "20.8.3.1", "bk_supplier_id": 0, "bk_cloud_id": 0}],
        "script_content": "ls",
        "script_param": "./",
        "script_timeout": 3000,
    }

    def setUp(self):
        self.job_client = utils.JobMockClient(
            fast_execute_script_return=utils.JOB_EXECUTE_TASK_RETURN,
            get_job_instance_log_return=utils.JOB_GET_INSTANCE_LOG_RETURN,
        )
        patch(utils.JOB_VERSION_MOCK_PATH, "V3").start()

    def component_cls(self):
        # return the component class which should be tested
        return JobFastExecuteScriptComponent

    def cases(self):
        # return your component test cases here
        return [
            ComponentTestCase(
                name="测试快速执行脚本成功",
                inputs=self.JOB_FAST_EXECUTE_SCRIPT,
                parent_data={},
                execute_assertion=ExecuteAssertion(
                    success=True, outputs={"job_instance_id": utils.TASK_ID, "polling_time": 0},
                ),
                schedule_assertion=ScheduleAssertion(
                    success=True,
                    outputs={"polling_time": 0, "task_result": self.TASK_RESULT, "job_instance_id": utils.TASK_ID},
                    callback_data=None,
                    schedule_finished=True,
                ),
                patchers=[Patcher(target=utils.JOB_CLIENT_MOCK_PATH, return_value=self.job_client)],
            )
        ]
