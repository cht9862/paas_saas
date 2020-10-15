# -*- coding: utf-8 -*-
from copy import deepcopy

from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from apps.backend.components.collections.agent import RunUpgradeCommandService, RunUpgradeCommandComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "开始执行升级脚本"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)

COMMON_INPUTS.update(
    {
        # Job插件需要的inputs参数
        "job_client": {
            "bk_biz_id": utils.DEFAULT_BIZ_ID_NAME["bk_biz_id"],
            "username": utils.DEFAULT_CREATOR,
            "os_type": constants.OsType.LINUX,
        },
        "ip_list": [{"bk_cloud_id": constants.DEFAULT_CLOUD, "ip": "20.8.3.1"}],
        "context": "test",
        "package_name": "gse_client-linux-x86_64_upgrade.tgz",
        "script_timeout": 10,
        "script_param": "test",
        "script_content": """cd "/usr/local/gse" && tar xf "/tmp/gse_client-linux-x86_64_upgrade.tgz" &&
    cd "/usr/local/gse/agent/bin" && ./gse_agent --reload""",
    }
)


class RunUpgradeCommandTestService(RunUpgradeCommandService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class RunUpgradeCommandTestComponent(RunUpgradeCommandComponent):
    bound_service = RunUpgradeCommandTestService


class PushUpgradePackageSuccessTest(TestCase, ComponentTestMixin):

    JOB_MOCK_CLIENT = utils.JobMockClient(
        fast_execute_script_return=utils.JOB_INSTANCE_ID_METHOD_RETURN,
        get_job_instance_log_return=utils.JOB_GET_INSTANCE_LOG_RETURN,
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 设置，默认接入点
        default_ap = models.AccessPoint.objects.get(name="默认接入点")
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(ap_id=default_ap.id)

        patch(utils.JOB_VERSION_MOCK_PATH, "V3").start()

    def component_cls(self):
        return RunUpgradeCommandTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试Linux Agent升级脚本成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={"job_instance_id": 10000, "polling_time": 0}),
                schedule_assertion=[
                    ScheduleAssertion(
                        success=True,
                        schedule_finished=True,
                        outputs={
                            "job_instance_id": 10000,
                            "polling_time": 0,
                            "task_result": {
                                "success": [
                                    {
                                        "ip": "20.8.3.1",
                                        "bk_cloud_id": 0,
                                        "log_content": "success",
                                        "error_code": 0,
                                        "exit_code": 0,
                                    }
                                ],
                                "pending": [],
                                "failed": [],
                            },
                        },
                    ),
                ],
                execute_call_assertion=None,
                patchers=[Patcher(target=utils.JOB_CLIENT_MOCK_PATH, return_value=self.JOB_MOCK_CLIENT)],
            )
        ]


class PushUpgradePackageWindowsSuccessTest(TestCase, ComponentTestMixin):

    JOB_MOCK_CLIENT = utils.JobMockClient(fast_execute_script_return=utils.JOB_INSTANCE_ID_METHOD_RETURN)

    WINDOW_CASE_INPUTS = deepcopy(COMMON_INPUTS)

    WINDOW_CASE_INPUTS.update(
        {
            "script_content": (
                "start gsectl.bat stop && ping -n 20 127.0.0.1 >> c:\\ping_ip.txt && "
                "C:\\tmp\\7z.exe x C:\\tmp\\gse_client-linux-x86_64_upgrade.tar "
                "-oC:\\tmp -y 1>nul 2>&1 && "
                "C:\\tmp\\7z.exe x C:\\tmp\\gse_client-linux-x86_64_upgrade.tar "
                "-aot -oc:\\gse -y 1>nul 2>&1 && gsectl.bat start"
            )
        }
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 设置，默认接入点
        default_ap = models.AccessPoint.objects.get(name="默认接入点")
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(ap_id=default_ap.id)
        # 更改安装主机的操作系统
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(os_type=constants.OsType.WINDOWS)
        patch(utils.JOB_VERSION_MOCK_PATH, "V3").start()

    def component_cls(self):
        return RunUpgradeCommandTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试Windows Agent升级脚本成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={"job_instance_id": 10000, "polling_time": 0}),
                schedule_assertion=[
                    ScheduleAssertion(
                        success=True,
                        schedule_finished=True,
                        # 如果是Windows，在该步骤无需查询作业状态
                        outputs={"job_instance_id": 10000, "polling_time": 0},
                    ),
                ],
                execute_call_assertion=None,
                patchers=[Patcher(target=utils.JOB_CLIENT_MOCK_PATH, return_value=self.JOB_MOCK_CLIENT)],
            )
        ]
