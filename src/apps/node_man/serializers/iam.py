# _*_ coding: utf-8 _*_
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from apps.node_man.constants import IAM_ACTION_DICT


class PermissionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(label=_("操作类型"), required=True, choices=list(IAM_ACTION_DICT.keys()),)
    instance_id = serializers.IntegerField(label=_("实例ID"), required=False)
    instance_name = serializers.CharField(label=_("实例名称"), required=False)


class ApplyPermissionSerializer(serializers.Serializer):
    apply_info = PermissionSerializer(label=_("申请权限信息"), many=True, required=True)
