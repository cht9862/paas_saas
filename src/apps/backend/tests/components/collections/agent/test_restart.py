# -*- coding: utf-8 -*-
from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
)

from apps.backend.components.collections.agent import RestartService, RestartComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "重启"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)

COMMON_INPUTS.update({"bk_username": utils.DEFAULT_CREATOR})

COMMON_INPUTS["host_info"]["bk_host_id"] = utils.BK_HOST_ID


class RestartTestService(RestartService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class RestartTestComponent(RestartComponent):
    bound_service = RestartTestService


class RestartLinuxAgentSuccessTest(TestCase, ComponentTestMixin):
    JOB_MOCK_CLIENT = utils.JobMockClient(
        fast_execute_script_return=utils.JOB_INSTANCE_ID_METHOD_V2_C_RETURN,
        get_job_instance_status_return=utils.GET_JOB_INSTANCE_STATUS_V2_C_RETURN,
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 设置，默认接入点
        default_ap = models.AccessPoint.objects.get(name="默认接入点")
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(ap_id=default_ap.id)
        patch(utils.CLIENT_V2_MOCK_PATH, self.JOB_MOCK_CLIENT).start()

    def component_cls(self):
        return RestartTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试重启Linux Agent成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]

    def tearDown(self):
        # 状态检查
        self.assertTrue(
            models.JobTask.objects.filter(bk_host_id=utils.BK_HOST_ID, current_step__endswith=DESCRIPTION).exists()
        )


class RestartWindowsAgentSuccessTest(RestartLinuxAgentSuccessTest):
    def setUp(self):
        super().setUp()
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(os_type=constants.OsType.WINDOWS)

    def cases(self):
        return [
            ComponentTestCase(
                name="测试重启Windows Agent成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]
