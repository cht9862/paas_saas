# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.node_man.serializers.iam import ApplyPermissionSerializer
from apps.node_man.handlers.iam import IamHandler
from apps.node_man.constants import IamActionType, IAM_ACTION_DICT
from apps.utils.local import get_request_username


class PermissionViewSet(APIViewSet):
    @action(detail=False, methods=["POST"], serializer_class=ApplyPermissionSerializer)
    def fetch(self, request, *args, **kwargs):
        """
        @api {POST} /permission/fetch/ 根据条件返回用户权限
        @apiName fetch_permission
        @apiGroup Permission
        @apiParam {Object[]} apply_info 申请权限信息
        @apiParam {String="cloud_edit", "cloud_delete", "cloud_view",
        "cloud_create", "ap_create", "ap_delete", "ap_edit"} apply_info.action 操作类型
        @apiParam {Int} apply_info.instance_id 实例ID
        @apiParam {String} apply_info.instance_name 实例名
        @apiSuccessExample {Json} 成功返回:
        [{
            "system": "节点管理",
            "action": "编辑云区域",
            "instance_id": 11,
            "instance_name": cloud_one,
            "apply_url": "https://xxx.com/.../"
        }]
        """

        redirect_url = IamHandler().fetch_redirect_url(self.validated_data["apply_info"], get_request_username())

        return Response(
            {
                "apply_info": [
                    {
                        "system": "节点管理",
                        "action": IAM_ACTION_DICT[param["action"]],
                        "instance_id": param.get("instance_id", -1),
                        "instance_name": param.get("instance_name", ""),
                    }
                    for param in self.validated_data["apply_info"]
                ],
                "url": redirect_url,
            }
        )

    @action(detail=False, methods=["GET"])
    def cloud(self, request, *args, **kwargs):
        """
        @api {GET} /permission/cloud/ 返回用户云区域的权限
        @apiName list_cloud_permission
        @apiGroup Permission
        @apiSuccessExample {Json} 成功返回:
        {
            "edit_action": [bk_cloud_ids],
            "delete_action": [bk_cloud_ids],
            "create_action": True or False,
        }
        """
        perms = IamHandler().fetch_policy(
            get_request_username(),
            [
                IamActionType.cloud_view,
                IamActionType.cloud_edit,
                IamActionType.cloud_delete,
                IamActionType.cloud_create,
            ],
        )
        return Response(
            {
                "view_action": perms[IamActionType.cloud_view],
                "edit_action": perms[IamActionType.cloud_edit],
                "delete_action": perms[IamActionType.cloud_delete],
                "create_action": perms[IamActionType.cloud_create],
            }
        )

    @action(detail=False, methods=["GET"])
    def ap(self, request, *args, **kwargs):
        """
        @api {GET} /permission/ap/ 返回用户接入点权限
        @apiName list_ap_permission
        @apiGroup Permission
        @apiSuccessExample {Json} 成功返回:
        {
            "edit_action": [ap_ids],
            "delete_action": [ap_ids],
            "create_action": True or False
        }
        """
        perms = IamHandler().fetch_policy(
            get_request_username(), [IamActionType.ap_edit, IamActionType.ap_delete, IamActionType.cloud_create]
        )

        return Response(
            {
                "edit_action": perms[IamActionType.ap_edit],
                "delete_action": perms[IamActionType.ap_delete],
                "create_action": perms[IamActionType.cloud_create],
            }
        )
