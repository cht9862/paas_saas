# -*- coding: utf-8 -*-
from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from apps.backend.components.collections.agent import PushUpgradePackageService, PushUpgradePackageComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "下发升级包"

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
        "ip_list": [{"bk_cloud_id": constants.DEFAULT_CLOUD, "ip": utils.TEST_IP}],
        "context": "test",
        # 由执行业务逻辑填充，在此只是展示数据结构
        "file_target_path": "/tmp/test",
        "file_source": [
            {
                "files": ["/tmp/REGEX:[a-z]*.txt"],
                "account": "root",
                "ip_list": [{"bk_cloud_id": constants.DEFAULT_CLOUD, "ip": utils.TEST_IP}],
                "custom_query_id": ["3"],
            }
        ],
    }
)


class PushUpgradePackageTestService(PushUpgradePackageService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class PushUpgradePackageTestComponent(PushUpgradePackageComponent):
    bound_service = PushUpgradePackageTestService


class PushUpgradePackageSuccessTest(TestCase, ComponentTestMixin):

    JOB_MOCK_CLIENT = utils.JobMockClient(
        fast_push_file_return=utils.JOB_INSTANCE_ID_METHOD_RETURN,
        get_job_instance_log_return=utils.JOB_GET_INSTANCE_LOG_RETURN,
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 设置，默认接入点
        default_ap = models.AccessPoint.objects.get(name="默认接入点")
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(ap_id=default_ap.id)

        patch(utils.JOB_VERSION_MOCK_PATH, "V3").start()

    def component_cls(self):
        return PushUpgradePackageTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="下发升级包成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(
                    success=True,
                    outputs={
                        "job_instance_id": 10000,
                        "polling_time": 0,
                        "package_name": "gse_client-linux-x86_64_upgrade.tgz",
                    },
                ),
                schedule_assertion=[
                    ScheduleAssertion(
                        success=True,
                        schedule_finished=True,
                        outputs={
                            "job_instance_id": 10000,
                            "polling_time": 0,
                            "package_name": "gse_client-linux-x86_64_upgrade.tgz",
                            "task_result": {
                                "success": [
                                    {
                                        "ip": utils.TEST_IP,
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
