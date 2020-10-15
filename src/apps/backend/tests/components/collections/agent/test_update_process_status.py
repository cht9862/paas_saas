# -*- coding: utf-8 -*-
from django.test import TestCase

from pipeline.component_framework.test import ComponentTestMixin, ComponentTestCase, ExecuteAssertion

from apps.backend.components.collections.agent import UpdateProcessStatusService, UpdateProcessStatusComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "更新主机进程状态"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)

# 设置需要更新的进程状态为NOT_INSTALLED
COMMON_INPUTS.update({"status": constants.ProcStateType.NOT_INSTALLED})


class UpdateProcessStatusTestService(UpdateProcessStatusService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class UpdateProcessStatusTestComponent(UpdateProcessStatusComponent):
    bound_service = UpdateProcessStatusTestService


class UpdateProcessStatusSuccessTest(TestCase, ComponentTestMixin):
    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 为验证更新主机状态时将node_from属性设置为nodeman
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(node_from=constants.NodeFrom.CMDB)

        # 创建主机对应进程状态UNKNOWN
        models.ProcessStatus.objects.create(
            bk_host_id=utils.BK_HOST_ID,
            name=models.ProcessStatus.GSE_AGENT_PROCESS_NAME,
            source_type=models.ProcessStatus.SourceType.DEFAULT,
            status=constants.ProcStateType.NOT_INSTALLED,
        )

    def component_cls(self):
        return UpdateProcessStatusTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="更新主机进程状态为NOT_INSTALLED成功",
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
        # 验证已修改进程状态
        self.assertTrue(
            models.ProcessStatus.objects.filter(
                bk_host_id=utils.BK_HOST_ID,
                name=models.ProcessStatus.GSE_AGENT_PROCESS_NAME,
                status=constants.ProcStateType.NOT_INSTALLED,
            ).exists()
        )
        # 验证未安装情况下主机node_from属性修改为CMDB
        self.assertTrue(
            models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID, node_from=constants.NodeFrom.CMDB).exists()
        )
