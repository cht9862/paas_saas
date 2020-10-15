# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class ListSerializer(serializers.Serializer):
    """
    用于云区域列表校验
    """

    with_default_area = serializers.BooleanField(label=_("是否返回直连区域"), required=False, default=False)


class EditSerializer(serializers.Serializer):
    """
    用于创建和更新云区域的验证
    """

    bk_cloud_name = serializers.CharField(label=_("云区域名称"))
    isp = serializers.CharField(label=_("云服务商"))
    ap_id = serializers.IntegerField(label=_("接入点ID"))
