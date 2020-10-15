# -*- coding: utf-8 -*-
from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import ComponentTestMixin, ComponentTestCase, ExecuteAssertion, ScheduleAssertion

from apps.backend.components.collections.agent import GetAgentStatusService, GetAgentStatusComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

DESCRIPTION = "查询 GSE 状态"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    attr_values={"description": DESCRIPTION, "bk_host_id": utils.BK_HOST_ID},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)

# 设置期望状态为RUNNING
COMMON_INPUTS.update({"expect_status": constants.PROC_STATUS_DICT[1]})

COMMON_INPUTS["host_info"]["bk_host_id"] = utils.BK_HOST_ID


class GetAgentStatusTestService(GetAgentStatusService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class GetAgentStatusTestComponent(GetAgentStatusComponent):
    bound_service = GetAgentStatusTestService


# 查询agent心跳详细信息。数据非实时，延时1分钟内
GET_AGENT_INFO_RETURN = {
    f"{constants.DEFAULT_CLOUD}:{utils.TEST_IP}": {
        "ip": utils.TEST_IP,
        "version": "V1.0.test",
        "bk_cloud_id": constants.DEFAULT_CLOUD,
        "parent_ip": "10.0.0.2",
        "parent_port": 80,
    }
}

# 查询agent实时在线状态
GET_AGENT_STATUS = {
    f"{constants.DEFAULT_CLOUD}:{utils.TEST_IP}": {
        "ip": utils.TEST_IP,
        "bk_cloud_id": constants.DEFAULT_CLOUD,
        "bk_agent_alive": 1,
    }
}


class GetRunningStatusSuccessTest(TestCase, ComponentTestMixin):
    GSE_MOCK_CLIENT = utils.GseMockClient(
        get_agent_status_return=GET_AGENT_STATUS, get_agent_info_return=GET_AGENT_INFO_RETURN,
    )

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        # 为验证更新主机状态时将node_from属性设置为nodeman
        models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID).update(node_from=constants.NodeFrom.CMDB)
        patch(utils.CLIENT_V2_MOCK_PATH, self.GSE_MOCK_CLIENT).start()

    def component_cls(self):
        return GetAgentStatusTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="查询Agent状态为RUNNING成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={}),
                schedule_assertion=[ScheduleAssertion(success=True, schedule_finished=True, outputs={})],
                execute_call_assertion=None,
                patchers=None,
            )
        ]

    def tearDown(self):
        # 状态检查
        self.assertTrue(
            models.JobTask.objects.filter(bk_host_id=utils.BK_HOST_ID, current_step__endswith=DESCRIPTION).exists()
        )
        # 验证Agent状态刷新
        self.assertTrue(
            models.ProcessStatus.objects.filter(
                bk_host_id=utils.BK_HOST_ID, version="V1.0.test", status=constants.PROC_STATUS_DICT[1]
            ).exists()
        )

        # 验证主机源修改
        self.assertTrue(
            models.Host.objects.filter(bk_host_id=utils.BK_HOST_ID, node_from=constants.NodeFrom.NODE_MAN).exists()
        )
