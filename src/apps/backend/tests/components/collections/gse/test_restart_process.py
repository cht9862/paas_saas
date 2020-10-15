# -*- coding: utf-8 -*-

from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)

from apps.backend.components.collections.gse import GseRestartProcessComponent
from apps.backend.api.constants import OS, GseDataErrCode
from apps.backend.tests.components.collections.gse import utils


class GseRestartProcessComponentTestCase(TestCase, ComponentTestMixin):
    GSE_CLIENT = {"username": "admin", "os_type": OS.LINUX}
    GSE_RESTART_PROCESS = {
        "gse_client": GSE_CLIENT,
        "proc_name": "sub_870_host_1_host_exp002",
        "hosts": [{"ip": "10.0.1.10", "bk_supplier_id": 0, "bk_cloud_id": 0}],
        "control": {
            "stop_cmd": "./stop.sh",
            "health_cmd": "",
            "reload_cmd": "./reload.sh",
            "start_cmd": "./start.sh",
            "version_cmd": "cat VERSION",
            "kill_cmd": "",
            "restart_cmd": "./restart.sh",
        },
        "exe_name": "host_exp002",
        "setup_path": "/usr/local/gse/external_plugins/sub_870_host_1/host_exp002",
        "pid_path": "/var/run/gse/sub_870_host_1/host_exp002.pid",
    }

    GSE_TASK_RESULT = {
        "success": [
            {
                "ip": "10.0.1.10",
                "bk_cloud_id": "0",
                "bk_supplier_id": "0",
                "error_code": GseDataErrCode.SUCCESS,
                "error_msg": "",
                "content": "",
            }
        ],
        "pending": [],
        "failed": [],
    }

    REGISTER_PROCESS_RESPONSE = {
        "message": "success",
        "code": 0,
        "data": {
            "0:0:10.0.1.10:nodeman:sub_870_host_1_host_exp002": {
                "content": "",
                "error_code": GseDataErrCode.SUCCESS,
                "error_msg": "",
            }
        },
        "result": True,
        "request_id": "1aebe780547a4ee296a15f4a19018aad",
    }

    def setUp(self):
        self.gse_client = utils.GseMockClient(
            update_proc_info_return=self.REGISTER_PROCESS_RESPONSE,
            operate_proc_return=utils.OPERATE_PROC_RETURN,
            get_proc_operate_result_return=self.REGISTER_PROCESS_RESPONSE,
        )

    def component_cls(self):
        # return the component class which should be tested
        return GseRestartProcessComponent

    def cases(self):
        # return your component test cases here
        result = [
            ComponentTestCase(
                name="测试重启主机进程成功",
                inputs=self.GSE_RESTART_PROCESS,
                parent_data={},
                execute_assertion=ExecuteAssertion(
                    success=True, outputs={"task_id": utils.TASK_ID, "polling_time": 0},
                ),
                schedule_assertion=ScheduleAssertion(
                    success=True,
                    outputs={"polling_time": 0, "task_result": self.GSE_TASK_RESULT, "task_id": utils.TASK_ID},
                    callback_data=None,
                    schedule_finished=True,
                ),
                patchers=[Patcher(target=utils.GSE_CLIENT_MOCK_PATH, return_value=self.gse_client)],
            )
        ]
        # mocker.stop()
        return result
