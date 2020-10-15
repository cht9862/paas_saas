# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from django.http import JsonResponse
from apps.generic import APIViewSet
from apps.node_man.handlers.tjj import TjjHandler


class TjjViews(APIViewSet):
    @action(methods=["post"], detail=False)
    def fetch_pwd(self, request, *args, **kwargs):
        """
        @api {POST} /tjj/fetch_pwd/  查询支持铁将军的主机
        @apiName fetch pwd
        @apiGroup Tjj
        @apiParam {String[]} hosts 主机IP
        @apiParamExample {Json} 请求参数
        {
            "hosts": [
                "x.x.x.x",
                "x.x.x.x"
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": True,
            "code": 0,
            "data": {
                "success_ips": ["x.x.x.x", "x.x.x.x"],
                "failed_ips": {
                    "x.x.x.x": {
                        "Code": 6,
                        "Message": "x.x.x.x不存在",
                        "Password": ""
                    }
                }
            },
            "message": "success"
        }
        """

        result = TjjHandler().fetch_pwd(
            request.user.username, request.data.get("hosts", []), request.COOKIES.get("TCOA_TICKET")
        )
        return JsonResponse(result)
