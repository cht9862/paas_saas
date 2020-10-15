# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.generic import GenericViewSet
from apps.node_man import constants as const


class ChoiceViewSet(GenericViewSet):
    @action(detail=False, methods=["get"])
    def os_type(self, request):
        """
        @api {GET} /choice/os_type/ 查询系统列表
        @apiName list_os_type
        @apiGroup choice
        @apiSuccessExample {json} 成功返回:
        [
            {
                "id": "LINUX",
                "name": "LINUX"
            },
            {
                "id": "WINDOWS",
                "name": "WINDOWS"
            },
            {
                "id": "AIX",
                "name": "AIX"
            }
        ]
        """
        return Response(
            {
                "result": True,
                "code": const.ResponseCodeStatus.OK,
                "message": u"success",
                "data": [dict(id=k, name=v) for k, v in const.OS_CHOICES],
            }
        )

    @action(detail=False, methods=["get"])
    def op(self, request):
        """
        @api {GET} /choice/op/ 查询操作列表
        @apiName list_op
        @apiGroup choice
        @apiSuccessExample {json} 成功返回:
        [
            {
                "id": "START",
                "name": "启动"
            },
            {
                "id": "STOP",
                "name": "停止"
            },
            ... ...
        ]
        """
        return Response(
            {"result": True, "code": const.ResponseCodeStatus.OK, "message": u"success", "data": const.FUNCTION_LIST}
        )

    @action(detail=False, methods=["get"])
    def category(self, request):
        """
        @api {GET} /choice/category/ 查询类别列表
        @apiName list_category
        @apiGroup choice
        @apiSuccessExample {json} 成功返回:
         [
            {
                "id": "official",
                "name": "官方插件"
            },
            {
                "id": "external",
                "name": "第三方插件"
            },
            {
                "id": "scripts",
                "name": "脚本插件"
            }
        ]
        """
        return Response(
            {"result": True, "code": const.ResponseCodeStatus.OK, "message": u"success", "data": const.CATEGORY_LIST}
        )

    @action(detail=False, methods=["get"])
    def job_type(self, request):
        """
        @api {GET} /choice/job_type/ 查询任务类型列表
        @apiName list_job_type
        @apiGroup choice
        @apiSuccessExample {json} 成功返回:
         [
            {
                "id": "INSTALL_PROXY",
                "name": "安装 ProxyPROXY"
            },
            {
                "id": "INSTALL_AGENT",
                "name": "安装 AgentAGENT"
            },
            {
                "id": "RESTART_PROXY",
                "name": "重启 ProxyPROXY"
            },
            ... ...
        ]
        """
        data = []
        for k in const.JOB_TUPLE:
            _k = k.split("_")
            obj = _k[1]
            v = const.JOB_TYPE_DICT.get(k) + obj
            row = {"id": k, "name": v}
            data.append(row)
        return Response({"result": True, "code": const.ResponseCodeStatus.OK, "message": u"success", "data": data})
