# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import base64
import hashlib

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.node_man import constants
from apps.node_man.models import GsePluginDesc, Packages


class GatewaySerializer(serializers.Serializer):
    bk_username = serializers.CharField()
    bk_app_code = serializers.CharField()


class PluginInfoSerializer(GatewaySerializer):
    """ 插件信息接口序列化器 """

    name = serializers.CharField(max_length=32)
    version = serializers.CharField(max_length=128, required=False)
    cpu_arch = serializers.CharField(max_length=32, allow_null=True, required=False)
    os = serializers.CharField(max_length=32, allow_null=True, required=False)

    def validate(self, attrs):
        # 检查插件是否存在
        try:
            plugin = GsePluginDesc.objects.get(name=attrs["name"])
        except GsePluginDesc.DoesNotExist:
            raise ValidationError("plugin {name} is not exist".format(name=attrs["name"]))
        attrs.pop("name")
        attrs["plugin"] = plugin

        return attrs


class ReleasePluginSerializer(GatewaySerializer):
    """ 发布插件序列化器 """

    id = serializers.ListField(child=serializers.IntegerField(), required=False, min_length=1)
    name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=128, required=False)
    cpu_arch = serializers.CharField(max_length=32, allow_null=True, required=False)
    os = serializers.CharField(max_length=32, allow_null=True, required=False)
    md5_list = serializers.ListField(child=serializers.CharField(), min_length=1)

    def validate(self, attrs):
        # id或name至少要有一个
        if not ("id" in attrs or ("name" in attrs and "version" in attrs)):
            raise ValidationError("at least has 'id' or ('name' + 'version')")

        return attrs


class CreatePluginConfigTemplateSerializer(GatewaySerializer):
    """ 创建插件配置模板 """

    plugin_name = serializers.CharField(max_length=32)
    plugin_version = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=32)
    version = serializers.CharField(max_length=128)
    format = serializers.CharField(max_length=16)
    file_path = serializers.CharField(max_length=128)
    content = serializers.CharField()
    md5 = serializers.CharField()
    is_release_version = serializers.BooleanField()

    def validate(self, attrs):
        # base64解码配置模板内容
        try:
            attrs["content"] = base64.b64decode(attrs["content"])
        except TypeError:
            raise ValidationError("content is not a valid base64 string")

        # 配置模板内容的md5是否匹配
        m = hashlib.md5()
        m.update(attrs["content"])
        if m.hexdigest() != attrs["md5"]:
            raise ValidationError("the md5 of content is not match")

        # 对应插件是否存在
        packages = Packages.objects.filter(project=attrs["plugin_name"])
        # 特殊版本不检查
        if attrs["plugin_version"] != "*":
            packages = packages.filter(version=attrs["plugin_version"])
        if not packages.exists():
            raise ValidationError(
                "plugin {plugin_name}:{plugin_version}".format(
                    plugin_name=attrs["plugin_name"], plugin_version=attrs["plugin_version"],
                )
            )
        attrs["content"] = attrs["content"].decode()

        return attrs


class ReleasePluginConfigTemplateSerializer(GatewaySerializer):
    """ 发布插件配置模板 """

    plugin_name = serializers.CharField(max_length=32, required=False)
    plugin_version = serializers.CharField(max_length=128, required=False)
    name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=32, required=False)
    id = serializers.ListField(child=serializers.IntegerField(), required=False, min_length=1)

    def validate(self, attrs):
        params_keys = {
            "plugin_name",
            "plugin_version",
        }

        # 两种参数模式少要有一种满足
        if not ("id" in attrs or len(params_keys - set(attrs.keys())) == 0):
            raise ValidationError("at least has 'id' or query params")

        return attrs


class RenderPluginConfigTemplateSerializer(GatewaySerializer):
    """ 渲染插件配置模板 """

    plugin_name = serializers.CharField(max_length=32, required=False)
    plugin_version = serializers.CharField(max_length=128, required=False)
    name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=32, required=False)
    id = serializers.IntegerField(required=False)
    data = serializers.DictField()

    def validate(self, attrs):
        params_keys = {"plugin_name", "plugin_version", "name", "version"}

        # 两种参数模式少要有一种满足
        if not ("id" in attrs or len(params_keys - set(attrs.keys())) == 0):
            raise ValidationError("at least has 'id' or query params")

        return attrs


class PluginConfigTemplateInfoSerializer(GatewaySerializer):
    """ 插件配置模板信息 """

    plugin_name = serializers.CharField(max_length=32, required=False)
    plugin_version = serializers.CharField(max_length=128, required=False)
    name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=32, required=False)
    id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        # 两种参数模式少要有一种满足
        if not ("id" in attrs or len(list(attrs.keys())) > 2):
            raise ValidationError("at least has 'id' or query params")

        return attrs


class PluginConfigInstanceInfoSerializer(GatewaySerializer):
    """ 插件配置实例信息 """

    plugin_name = serializers.CharField(max_length=32, required=False)
    plugin_version = serializers.CharField(max_length=128, required=False)
    name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=32, required=False)
    id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        # 两种参数模式少要有一种满足
        if not ("id" in attrs or len(list(attrs.keys())) > 2):
            raise ValidationError("at least has 'id' or query params")

        return attrs


class UploadInfoSerializer(GatewaySerializer):
    """上传插件包接口序列化器"""

    module = serializers.CharField(max_length=32)
    md5 = serializers.CharField(max_length=32)
    file_name = serializers.CharField()
    file_local_path = serializers.CharField(max_length=512)
    file_local_md5 = serializers.CharField(max_length=32)


class PluginStartDebugSerializer(GatewaySerializer):
    """
    启动调试参数信息
    """

    class HostInfoSerializer(serializers.Serializer):
        ip = serializers.CharField(required=True)
        bk_cloud_id = serializers.IntegerField(required=True)
        bk_supplier_id = serializers.IntegerField(default=constants.DEFAULT_SUPPLIER_ID)
        bk_biz_id = serializers.IntegerField(required=True)

    plugin_id = serializers.IntegerField(required=False)
    plugin_name = serializers.CharField(max_length=32, required=False)
    version = serializers.CharField(max_length=32, required=False)
    config_ids = serializers.ListField(default=[], allow_empty=True, child=serializers.IntegerField())
    host_info = HostInfoSerializer(required=True)

    def validate(self, attrs):
        # 两种参数模式少要有一种满足
        if "id" not in attrs and not ("plugin_name" in attrs and "version") in attrs:
            raise ValidationError("`plugin_id` or `plugin_name + version` required")

        return attrs


class PluginRegisterSerializer(GatewaySerializer):

    file_name = serializers.CharField()
    is_release = serializers.BooleanField()


class PluginRegisterTaskSerializer(GatewaySerializer):

    job_id = serializers.IntegerField()


class ExportSerializer(GatewaySerializer):
    """
    导出包序列化器
    """

    class GsePluginParamsSerializer(serializers.Serializer):
        """
        Gse 采集器序列化器
        """

        project = serializers.CharField()
        # 版本号不做正则校验，原因是各个版本指定规则不一，不好统一限制
        # 考虑应该通过DB查询进行进一步的限制即可
        version = serializers.CharField()

    category = serializers.CharField()
    query_params = GsePluginParamsSerializer()
    creator = serializers.CharField()
    bk_app_code = serializers.CharField()


class DeletePluginSerializer(GatewaySerializer):
    name = serializers.CharField()
