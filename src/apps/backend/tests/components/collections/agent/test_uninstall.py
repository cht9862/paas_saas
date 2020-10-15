# -*- coding: utf-8 -*-
from copy import deepcopy

from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
)

from apps.backend.api.constants import JobDataStatus
from apps.backend.components.collections.agent import UninstallService, UninstallComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "下发卸载脚本命令"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)

COMMON_INPUTS.update(
    {"is_uninstall": True, "bk_username": utils.DEFAULT_CREATOR, "success_callback_step": "uninstall agent"}
)


class UninstallTestService(UninstallService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class UninstallTestComponent(UninstallComponent):
    bound_service = UninstallTestService


class UninstallAgentSuccessTest(TestCase, ComponentTestMixin):
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
        return UninstallTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试卸载Agent成功",
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


class UninstallWindowsAgentSuccessTest(UninstallAgentSuccessTest):
    def setUp(self):
        super().setUp()
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(os_type=constants.OsType.WINDOWS)

    def cases(self):
        return [
            ComponentTestCase(
                name="测试卸载Windows Agent成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]


class UninstallAgentFailTest(TestCase, ComponentTestMixin):
    # 设置查询到作业失败的情况
    GET_JOB_INSTANCE_STATUS_FAIL_RETURN = deepcopy(utils.GET_JOB_INSTANCE_STATUS_V2_C_RETURN)
    GET_JOB_INSTANCE_STATUS_FAIL_RETURN["job_instance"]["status"] = JobDataStatus.FAILED
    JOB_MOCK_CLIENT = utils.JobMockClient(
        fast_execute_script_return=utils.JOB_INSTANCE_ID_METHOD_V2_C_RETURN,
        get_job_instance_status_return=GET_JOB_INSTANCE_STATUS_FAIL_RETURN,
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 设置，默认接入点
        default_ap = models.AccessPoint.objects.get(name="默认接入点")
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(ap_id=default_ap.id)
        patch(utils.CLIENT_V2_MOCK_PATH, self.JOB_MOCK_CLIENT).start()

    def component_cls(self):
        return UninstallTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试卸载Agent失败",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=False, outputs={}),
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
