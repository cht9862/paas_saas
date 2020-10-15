# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.node_man.handlers.plugin import PluginHandler
from apps.node_man.models import GsePluginDesc, Host, Packages, ProcessStatus
from apps.node_man.serializers.plugin import (
    GsePluginSerializer,
    OperateSerializer,
    PluginListSerializer,
    ProcessPackageSerializer,
    ProcessStatusSerializer,
)
from apps.utils.local import get_request_username


class GsePluginViewSet(ModelViewSet):
    """
    获取agent运行状态和版本信息
    """

    model = GsePluginDesc
    queryset = GsePluginDesc.objects.all().order_by("-id")
    serializer_class = GsePluginSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        category = self.kwargs.get("category")
        if category is not None:
            self.queryset = self.queryset.filter(category=category)
        return self.queryset

    def list(self, *args, **kwargs):
        """
        @api {GET} /plugin/{{pk}}/process/ 查询插件列表,pk为official, external 或 scripts
        @apiName list_process
        @apiGroup plugin
        @apiSuccessExample {json} 成功返回:
        [{
            "id":14,
            "name":"bklogbeat",
            "description":"windows日志文件采集",
            "description_en":"Windows log collector",
            "scenario":"数据平台，蓝鲸监控，日志检索等和日志相关的数据. 首次使用插件管理进行操作前，先到日志检索/数据平台等进行设置插件的功能项",
            "scenario_en":"Log collection on data, bkmonitor, log-search apps",
            "category":"official",
            "config_file":"bklogbeat.conf",
            "config_format":"yaml",
            "use_db":false,
            "is_binary":true,
            "auto_launch":false
        }]
        """
        return super().list(*args, **kwargs)


class PluginViewSet(ModelViewSet):
    model = Host

    @action(detail=False, methods=["POST"])
    def search(self, request):
        """
        @api {POST} /plugin/search/ 查询插件列表
        @apiName list_host
        @apiGroup plugin
        @apiParam {Int[]} [bk_biz_id] 业务ID
        @apiParam {Int[]} [bk_host_id] 主机ID
        @apiParam {List} [conditions] 搜索条件，支持os_type, ip, status <br>
        version, bk_cloud_id, node_from 和 模糊搜索query
        @apiParam {Int[]} [exclude_hosts] 跨页全选排除主机
        @apiParam {Int} [page] 当前页数
        @apiParam {Int} [pagesize] 分页大小
        @apiParam {Boolean} [only_ip] 只返回IP
        @apiSuccessExample {json} 成功返回:
        {
            "total": 188,
            "list": [
                {
                    "bk_cloud_id": 1,
                    "bk_cloud_name": "云区域名称",
                    "bk_biz_id": 2,
                    "bk_biz_name": "业务名称",
                    "bk_host_id": 1,
                    "os_type": "linux",
                    "inner_ip": "127.0.0.1",
                    "plugin_status": {}
                    "job_result": {
                        "job_id": 1,
                        "status": "FAILED",
                        "current_step": "下载安装包",
                    }
                }
            ]
        }
        """

        # 校验
        self.serializer_class = PluginListSerializer
        data = self.validated_data

        # 处理
        hosts = PluginHandler.list(data)
        return Response(hosts)

    @action(detail=False, methods=["POST"], serializer_class=OperateSerializer)
    def operate(self, request):
        """
        @api {POST} /plugin/operate/ 插件操作类任务
        @apiDescription 用于插件的各类操作。<br>
        bk_host_id和exclude_hosts必填一个。<br>
        若填写了 exclude_hosts ，则代表跨页全选模式。<br>
        注意, 云区域ID、业务ID等筛选条件，仅在跨页全选模式下有效。<br>
        @apiName operate_plugin
        @apiGroup plugin
        @apiParam {String} job_type 任务类型
        @apiParam {Object[]} plugin_params 插件信息
        @apiParam {String} plugin_params.name 插件名称
        @apiParam {String} [plugin_params.version] 插件版本
        @apiParam {String} [plugin_params.keep_config] 插件版本
        @apiParam {String} [plugin_params.no_restart] 插件版本
        @apiParam {String} [bk_biz_id] 业务ID
        @apiParam {List} [condition] 搜索条件，支持os_type, ip, status <br>
        version, bk_cloud_id, node_from 和 模糊搜索query
        @apiParam {Int[]} [exclude_hosts] 跨页全选排除主机
        @apiParam {Int[]} [bk_host_id] 主机ID
        主机ID和跨页全选排除主机必选一个
        @apiParamExample {Json} 安装请求参数
        {
            "job_type": "START_PLUGIN",
            "bk_host_id": [7731, 7732],
            "plugin_params": {
                "name": "basereport",
                "version": "10.1.12"
            }
        }
        """
        return Response(PluginHandler.operate(self.validated_data, get_request_username(), request.user.is_superuser))

    @action(detail=False, methods=["GET"])
    def statistics(self, request):
        """
        @api {GET} /plugin/statistics/ 获取插件统计数据
        @apiDescription 根据业务、插件、版本等维度，统计插件在主机的安装数量
        @apiName plugin_statistics
        @apiGroup plugin
        @apiSuccessExample {json} 成功返回:
        [
            {
                "bk_biz_id": 2,
                "plugin_name": "basereport",
                "version": "1.2.3",
                "host_count": 1
            },
            {
                "bk_biz_id": 2,
                "plugin_name": "processbeat",
                "version": "10.1.2",
                "host_count": 2
            }
        ]
        """
        return Response(PluginHandler.get_statistics())


class PackagesViews(ModelViewSet):
    model = Packages
    serializer_class = ProcessPackageSerializer

    def list(self, request, *args, **kwargs):
        """
        @api {GET} /plugin/{{pk}}/package/ 查询进程包列表,pk为具体进程名
        @apiName list_package
        @apiGroup plugin
        @apiParam {String} os 系统类型
        @apiSuccessExample {json} 成功返回:
        [
                {
                    "id":2,
                    "pkg_name":"basereport-10.1.12.tgz",
                    "version":"10.1.12",
                    "module":"gse_plugin",
                    "project":"basereport",
                    "pkg_size":4561957,
                    "pkg_path":"/data/bkee/miniweb/download/linux/x86_64",
                    "md5":"046779753b6709635db0c861a1b0020e",
                    "pkg_mtime":"2019-11-01 20:46:52.404139",
                    "pkg_ctime":"2019-11-01 20:46:52.404139",
                    "location":"http://x.x.x.x/download/linux/x86_64",
                    "os":"linux",
                    "cpu_arch":"x86_64"
                },
                {
                    "id":1,
                    "pkg_name":"basereport-10.1.9.tgz",
                    "version":"10.1.9",
                    "module":"gse_plugin",
                    "project":"basereport",
                    "pkg_size":4562217,
                    "pkg_path":"/data/bkee/miniweb/download/linux/x86_64",
                    "md5":"6fe084f450352b1fa598a41a72800bc8",
                    "pkg_mtime":"2019-08-26 19:17:56.905309",
                    "pkg_ctime":"2019-08-26 19:17:56.905309",
                    "location":"http://x.x.x.x/download/linux/x86_64",
                    "os":"linux",
                    "cpu_arch":"x86_64"
                }
            ]
        """
        project = kwargs["process"]
        os_type = request.query_params.get("os", "")
        queryset = PluginHandler.get_packages(project, os_type)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProcessStatusViewSet(ModelViewSet):
    model = ProcessStatus
    serializer_class = ProcessStatusSerializer

    @action(methods=["POST"], detail=False, url_path="status")
    def process_status(self, request, *args, **kwargs):
        """
        @api {POST} /plugin/process/status/ 查询主机进程状态信息
        @apiName list_process_status
        @apiGroup plugin
        @apiParam {Int[]} bk_host_ids 主机ID
        @apiSuccessExample {json} 请求示例:
        {
            "bk_host_ids": [1,2]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
            "data": [
                {
                    "bk_host_id": 1,
                    "name": "gseagent",
                    "status": "RUNNING",
                    "version": "1.60.54"
                },
                {
                    "bk_host_id": 2,
                    "name": "gseagent",
                    "status": "RUNNING",
                    "version": "1.60.54"
                }
            ]
        }
        """
        bk_host_ids = request.data.get("bk_host_ids", [])
        queryset = PluginHandler.get_process_status(bk_host_ids)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
