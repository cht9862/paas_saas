from rest_framework import permissions
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from apps.node_man.models import Cloud
from apps.node_man.constants import IamActionType
from apps.node_man.handlers.iam import IamHandler
from apps.node_man.exceptions import CloudNotExistError
from apps.utils.local import get_request_username


class GlobalSettingPermission(permissions.BasePermission):
    """
    全局配置权限控制
    """

    message = _("您没有权限执行操作")

    def has_permission(self, request, view):
        # 接入点编辑、删除、创建权限

        if view.action in ["list", "ap_is_using"]:
            # List接口不需要鉴权
            return True

        # 若没有使用权限中心
        if not settings.USE_IAM:
            if IamHandler.is_superuser(get_request_username()):
                return True
            else:
                self.message = _("您没有该接入点的权限")
                return False

        # 使用权限中心
        perms = IamHandler().fetch_policy(
            get_request_username(),
            [IamActionType.ap_edit, IamActionType.ap_delete, IamActionType.ap_create, IamActionType.ap_view],
        )

        if view.action in ["create", "test"] and perms[IamActionType.ap_create]:
            return True

        if view.action == "update" and int(view.kwargs.get("pk", 0)) in perms[IamActionType.ap_edit]:
            return True

        if view.action == "destroy" and int(view.kwargs.get("pk", 0)) in perms[IamActionType.ap_delete]:
            return True

        if view.action == "retrieve" and int(view.kwargs.get("pk", 0)) in perms[IamActionType.ap_view]:
            return True

        message_dict = {
            "create": _("您没有创建接入点的权限"),
            "update": _("您没有编辑该接入点的权限"),
            "destroy": _("您没有删除该接入点的权限"),
            "view": _("您没有查看该接入点详情的权限"),
        }

        self.message = message_dict.get(view.action, "您没有相应操作的权限")
        return False


class CloudPermission(permissions.BasePermission):
    """
    云区域权限控制
    """

    message = _("您没有权限执行操作")

    def has_permission(self, request, view):
        # 云区域查看、编辑、删除、创建权限

        if view.action == "list":
            # List接口不需要鉴权
            return True

        # **若没有使用权限中心**
        if not settings.USE_IAM:

            # 任何人都有创建云区域权限
            if view.action == "create":
                return True

            # 只有创建者和超管才有云区域详情、编辑、删除权限
            try:
                cloud = Cloud.objects.get(pk=int(view.kwargs.get("pk", -1)))
            except Cloud.DoesNotExist:
                raise CloudNotExistError(_("不存在ID为: {bk_cloud_id} 的云区域").format(bk_cloud_id=int(view.kwargs.get("pk"))))

            if get_request_username() in cloud.creator or IamHandler.is_superuser(get_request_username()):
                return True
            else:
                return False

        # **使用了权限中心**
        perms = IamHandler().fetch_policy(
            get_request_username(),
            [
                IamActionType.cloud_view,
                IamActionType.cloud_edit,
                IamActionType.cloud_delete,
                IamActionType.cloud_create,
            ],
        )

        if perms[IamActionType.cloud_create] and view.action == "create":
            return True

        if int(view.kwargs.get("pk", 0)) in perms[IamActionType.cloud_view] and view.action == "retrieve":
            return True

        if int(view.kwargs.get("pk", 0)) in perms[IamActionType.cloud_edit] and view.action == "update":
            return True

        if int(view.kwargs.get("pk", 0)) in perms[IamActionType.cloud_delete] and view.action == "destroy":
            return True

        message_dict = {
            "create": _("您没有创建云区域的权限"),
            "update": _("您没有编辑该云区域的权限"),
            "destroy": _("您没有删除该云区域的权限"),
            "retrieve": _("您没有查看该云区域详情的权限"),
        }

        self.message = message_dict.get(view.action, "您没有相应操作的权限")
        return False


class DebugPermission(permissions.BasePermission):
    """
    Debug接口权限控制
    """

    message = _("您没有查询Debug接口的权限")

    def has_permission(self, request, view):
        # Debug接口权限控制，超管用户才有权限

        if IamHandler.is_superuser(get_request_username()):
            return True
        else:
            return False
