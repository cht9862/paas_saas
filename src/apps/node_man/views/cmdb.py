# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.utils.local import get_request_username
from apps.node_man.handlers.cmdb import CmdbHandler
from apps.node_man.serializers.host import FetchTopoSerializer
from apps.node_man.serializers.cmdb import BizSerializer


class CmdbViews(APIViewSet):
    @action(detail=False)
    def biz(self, request, *args, **kwargs):
        """
        @api {GET} /cmdb/biz/  查询用户所有业务
        @apiName retrieve_biz
        @apiGroup cmdb
        @apiParam {String="agent_view", "agent_operate", "proxy_operate",
        "plugin_view", "plugin_operate", "task_history_view"} action 操作类型
        @apiSuccessExample {json} 成功返回:
        [{
            "bk_biz_id": "50",
            "bk_biz_name": "蓝鲸XX"
        }]
        """

        # 校验
        self.serializer_class = BizSerializer
        data = self.validated_data

        data_list = CmdbHandler().biz(data)
        return Response(data_list)

    @action(detail=False, methods=["GET"])
    def fetch_topo(self, request, *args, **kwargs):
        """
        @api {GET} /cmdb/fetch_topo/ 获得拓扑信息
        @apiName fetch_topo
        @apiGroup cmdb
        @apiParam {Int} bk_biz_id 主机ID
        @apiSuccessExample {json} 成功返回:
        [{
            "bk_set_name": "空闲机池",
            "bk_set_id": 2,
            "modules": [
                {
                    "bk_module_name": "空闲机",
                    "bk_module_id": 3
                },
                {
                    "bk_module_name": "故障机",
                    "bk_module_id": 4
                }
            ]
        }]
        """

        # 校验
        self.serializer_class = FetchTopoSerializer
        data = self.validated_data

        # 处理
        return Response(CmdbHandler().fetch_topo(data, get_request_username(), request.user.is_superuser))
