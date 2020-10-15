# -*- coding: utf-8 -*-
from copy import deepcopy

from mock import patch
from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
)

from apps.backend.components.collections.agent import RegisterHostService, RegisterHostComponent
from apps.backend.tests.components.collections.agent import utils
from apps.node_man import models, constants

SEARCH_BUSINESS_RESULT = {
    "count": 1,
    "info": [
        {
            "bk_biz_id": utils.DEFAULT_BIZ_ID_NAME["bk_biz_id"],
            "default": 0,
            "bk_biz_name": utils.DEFAULT_BIZ_ID_NAME["bk_biz_name"],
            "bk_biz_maintainer": utils.DEFAULT_CREATOR,
        }
    ],
}

SEARCH_HOST_RESULT = {
    "count": 1,
    "info": [
        {
            "host": {
                "bk_host_id": utils.BK_HOST_ID,
                "bk_cloud_id": [
                    {
                        "bk_obj_name": "",
                        "id": "0",
                        "bk_obj_id": "plat",
                        "bk_obj_icon": "",
                        "bk_inst_id": 0,
                        "bk_inst_name": "default area",
                    }
                ],
            },
            "set": [],
            "biz": [
                {
                    "bk_biz_id": utils.DEFAULT_BIZ_ID_NAME["bk_biz_id"],
                    "default": 0,
                    "bk_biz_name": utils.DEFAULT_BIZ_ID_NAME["bk_biz_name"],
                }
            ],
            "module": [],
        }
    ],
}

DESCRIPTION = "注册主机到配置平台"

COMMON_INPUTS = utils.AgentTestObjFactory.inputs(
    # bk_host_id 设置为空
    attr_values={"description": DESCRIPTION},
    # 主机信息保持和默认一致
    instance_info_attr_values={},
)


class RegisterHostTestService(RegisterHostService):
    id = utils.JOB_TASK_PIPELINE_ID
    root_pipeline_id = utils.INSTANCE_RECORD_ROOT_PIPELINE_ID


class RegisterHostTestComponent(RegisterHostComponent):
    bound_service = RegisterHostTestService


class RegisterHostSuccessTest(TestCase, ComponentTestMixin):
    CMDB_MOCK_CLIENT = None

    def setUp(self):
        utils.AgentTestObjFactory.init_db()
        self.CMDB_MOCK_CLIENT = utils.CMDBMockClient(
            add_host_to_resource_result={"count": 1},
            search_business_result=SEARCH_BUSINESS_RESULT,
            search_host_result=SEARCH_HOST_RESULT,
        )
        patch(utils.CLIENT_V2_MOCK_PATH, self.CMDB_MOCK_CLIENT).start()

    def component_cls(self):
        return RegisterHostTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试注册主机成功",
                inputs=COMMON_INPUTS,
                parent_data={},
                execute_assertion=ExecuteAssertion(success=True, outputs={"bk_host_id": utils.BK_HOST_ID}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]

    def tearDown(self):
        # 安装任务，进程状态刚刚创建，状态是未安装
        self.assertTrue(
            models.ProcessStatus.objects.filter(
                bk_host_id=utils.BK_HOST_ID, status=constants.ProcStateType.NOT_INSTALLED
            ).exists()
        )

        # 检查是否在 subscription_instance_record.instance_info.host中新增bk_host_id字段
        bk_host_id = models.SubscriptionInstanceRecord.objects.get(
            pipeline_id=utils.INSTANCE_RECORD_ROOT_PIPELINE_ID
        ).instance_info["host"]["bk_host_id"]
        self.assertEqual(bk_host_id, utils.BK_HOST_ID)


class RegisterHostFailTest(TestCase, ComponentTestMixin):
    CMDB_MOCK_CLIENT = None

    def setUp(self):
        utils.AgentTestObjFactory.init_db()

        search_host_registered_result = deepcopy(SEARCH_HOST_RESULT)
        # 主机已被注册到bk_biz_id=1的业务
        search_host_registered_result["info"][0]["biz"][0]["bk_biz_id"] = 1
        self.CMDB_MOCK_CLIENT = utils.CMDBMockClient(
            add_host_to_resource_result={"count": 1},
            search_business_result=SEARCH_BUSINESS_RESULT,
            search_host_result=search_host_registered_result,
        )
        patch(utils.CLIENT_V2_MOCK_PATH, self.CMDB_MOCK_CLIENT).start()

    def component_cls(self):
        return RegisterHostTestComponent

    def cases(self):
        return [
            ComponentTestCase(
                name="测试注册主机失败，已被其他业务占用",
                inputs=COMMON_INPUTS,
                parent_data={},
                # 主机注册失败，output不存在bk_host_id
                execute_assertion=ExecuteAssertion(success=False, outputs={}),
                schedule_assertion=None,
                execute_call_assertion=None,
                patchers=None,
            )
        ]

    def tearDown(self):
        # 主机注册失败.
        self.assertFalse(
            models.ProcessStatus.objects.filter(
                bk_host_id=utils.BK_HOST_ID, status=constants.ProcStateType.NOT_INSTALLED
            ).exists()
        )
