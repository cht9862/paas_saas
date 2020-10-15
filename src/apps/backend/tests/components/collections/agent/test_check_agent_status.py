# -*- coding: utf-8 -*-
from django.test import TestCase

from pipeline.component_framework.test import ComponentTestMixin, ComponentTestCase, ExecuteAssertion

from apps.backend.components.collections.agent import CheckAgentStatusService, CheckAgentStatusComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "检查Agent状态"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)


class CheckAgentStatusTestService(CheckAgentStatusService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class CheckAgentStatusTestComponent(CheckAgentStatusComponent):
    bound_service = CheckAgentStatusTestService


class CheckAgentNormalStatusTest(TestCase, ComponentTestMixin):
    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        models.ProcessStatus.objects.create(
            bk_host_id=utils.BK_HOST_ID,
            name=models.ProcessStatus.GSE_AGENT_PROCESS_NAME,
            source_type=models.ProcessStatus.SourceType.DEFAULT,
            # 设置正常的Agent状态
            status=constants.ProcStateType.RUNNING,
        )

    def component_cls(self):
        return CheckAgentStatusTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试检查正常的Agent状态",
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


class CheckAgentStatusFailTest(CheckAgentNormalStatusTest):
    def setUp(self):
        super().setUp()
        # 将主机进程更新为一个不正常的状态
        models.ProcessStatus.objects.filter(
            bk_host_id=utils.BK_HOST_ID, name=models.ProcessStatus.GSE_AGENT_PROCESS_NAME
        ).update(status=constants.ProcStateType.NOT_INSTALLED)

    def cases(self):
        return [
            ComponentTestCase(
                name="测试检查异常的Agent状态",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=False, outputs={}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]
