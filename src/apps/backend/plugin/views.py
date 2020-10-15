# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import base64
import hashlib
import logging
import ntpath
import os
import posixpath
from copy import deepcopy

import six
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.backend.exceptions import JobNotExistError, StopDebugError, UploadPackageNotExistError
from apps.backend.plugin import manager, tasks
from apps.backend.plugin.serializers import (
    CreatePluginConfigTemplateSerializer,
    DeletePluginSerializer,
    ExportSerializer,
    PluginConfigInstanceInfoSerializer,
    PluginConfigTemplateInfoSerializer,
    PluginInfoSerializer,
    PluginRegisterSerializer,
    PluginRegisterTaskSerializer,
    PluginStartDebugSerializer,
    ReleasePluginConfigTemplateSerializer,
    ReleasePluginSerializer,
    RenderPluginConfigTemplateSerializer,
    UploadInfoSerializer,
)
from apps.generic import APIViewSet
from apps.node_man import constants as const
from apps.node_man import models
from apps.node_man.models import ProcessStatus
from apps.node_man.serializers import misc
from apps.utils import env
from blueapps.account.decorators import login_exempt

logger = logging.getLogger("app")

# 接口到序列化器的映射关系
PluginAPISerializerClasses = dict(
    info=PluginInfoSerializer,
    release=ReleasePluginSerializer,
    create_config_template=CreatePluginConfigTemplateSerializer,
    release_config_template=ReleasePluginConfigTemplateSerializer,
    render_config_template=RenderPluginConfigTemplateSerializer,
    query_config_template=PluginConfigTemplateInfoSerializer,
    query_config_instance=PluginConfigInstanceInfoSerializer,
    start_debug=PluginStartDebugSerializer,
    create_plugin_register_task=PluginRegisterSerializer,
    query_plugin_register_task=PluginRegisterTaskSerializer,
    delete=DeletePluginSerializer,
    create_export_task=ExportSerializer,
)


class PluginViewSet(APIViewSet):
    """
    插件相关API
    """

    queryset = ""
    # permission_classes = (BackendBasePermission,)

    def get_validated_data(self):
        """
        使用serializer校验参数，并返回校验后参数
        :return: dict
        """
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data

        # 从 esb 获取参数
        bk_username = self.request.META.get("HTTP_BK_USERNAME")
        bk_app_code = self.request.META.get("HTTP_BK_APP_CODE")

        data = data.copy()
        data.setdefault("bk_username", bk_username)
        data.setdefault("bk_app_code", bk_app_code)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return deepcopy(serializer.validated_data)

    def get_serializer_class(self):
        """
        根据方法名返回合适的序列化器
        """
        return PluginAPISerializerClasses.get(self.action)

    """
    触发注册插件包及查询任务状态
    """

    @action(detail=False, methods=["POST"], url_path="create_register_task")
    def create_plugin_register_task(self, request):
        """
        @api {POST} /plugin/create_register_task/ 创建注册任务
        @apiName create_register_task
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        file_name = params["file_name"]

        # 1. 判断是否存在需要注册的文件信息
        models_queryset = models.UploadPackage.objects.filter(file_name=file_name)
        if not models_queryset.exists():
            raise UploadPackageNotExistError(_("找不到请求发布的文件，请确认后重试"))

        # 2. 创建一个新的task,返回任务ID
        job = models.Job.objects.create(
            created_by=params["bk_username"],
            job_type=const.JobType.PACKING_PLUGIN,
            # TODO 打包任务是否也用一次性订阅的方式下发
            subscription_id=-1,
            status=const.JobStatusType.RUNNING,
        )
        # 这个新的任务，应该是指派到自己机器上的打包任务
        tasks.package_task.delay(job.id, params)
        logger.info("create job->[{}] to unpack file->[{}] plugin".format(job.id, file_name))

        return Response({"job_id": job.id})

    @action(detail=False, methods=["GET"], url_path="query_register_task")
    def query_plugin_register_task(self, request):
        """
        @api {GET} /plugin/query_register_task/ 查询插件注册任务
        @apiName query_register_task
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        job_id = params["job_id"]

        # 寻找这个任务对应的job_task
        try:
            job_task = models.Job.objects.get(id=job_id)

        except models.Job.DoesNotExist:
            logger.error("user try to query job->[%s] but is not exists." % job_id)
            raise JobNotExistError(_("找不到请求的任务，请确认后重试"))

        return Response(
            {
                "is_finish": job_task.end_time is not None,
                "status": job_task.status,
                "message": ""
                # TODO 任务日志
                # "message": models.TaskLog.get_log(job_id=job_id)
            }
        )

    @action(detail=False, methods=["GET"], url_path="info")
    def info(self, request):
        """
        @api {GET} /plugin/info/ 查询插件信息
        @apiName query_plugin_info
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        plugin = params.pop("plugin")
        bk_username = params.pop("bk_username")
        bk_app_code = params.pop("bk_app_code")

        plugin_packages = plugin.get_packages(**params)

        result = []

        for package in plugin_packages:
            result.append(
                dict(
                    id=package.id,
                    name=plugin.name,
                    os=package.os,
                    cpu_arch=package.cpu_arch,
                    version=package.version,
                    is_release_version=package.is_release_version,
                    is_ready=package.is_ready,
                    pkg_size=package.pkg_size,
                    md5=package.md5,
                    location=package.location,
                    creator=bk_username,
                    source_app_code=bk_app_code,
                )
            )

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="release")
    def release(self, request):
        """
        @api {POST} /plugin/release/ 发布插件
        @apiName release_plugin
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        params.pop("bk_username")
        params.pop("bk_app_code")

        try:
            if "id" in params:
                plugin_packages = models.GsePluginDesc.release_plugin(params["md5_list"], package_ids=params["id"])
            else:
                plugin_packages = models.GsePluginDesc.release_plugin(params.pop("md5_list"), query_params=params)
        except ValueError as e:
            raise ValidationError(e)

        return Response([package.id for package in plugin_packages])

    @action(detail=False, methods=["POST"], url_path="delete")
    def delete(self, request):
        """
        @api {POST} /plugin/delete/ 删除插件
        @apiName delete_plugin
        @apiGroup backend_plugin
        """
        # TODO: 完成采集配置后需要添加检测逻辑
        params = self.get_validated_data()
        params.pop("bk_username")
        params.pop("bk_app_code")
        name = params["name"]

        models.GsePluginDesc.objects.filter(name=name).delete()
        packages = models.Packages.objects.filter(project=name)
        for package in packages:
            file_path = os.path.join(package.pkg_path, package.pkg_name)
            if os.path.exists(file_path):
                os.remove(file_path)

        packages.delete()
        models.ProcControl.objects.filter(project=name).delete()
        plugin_templates = models.PluginConfigTemplate.objects.filter(plugin_name=name)
        models.PluginConfigInstance.objects.filter(
            plugin_config_template__in=[template.id for template in plugin_templates]
        ).delete()

        return Response()

    @action(detail=False, methods=["POST"], url_path="create_config_template")
    def create_config_template(self, request):
        """
        @api {POST} /plugin/create_config_template/ 创建配置模板
        @apiName create_plugin_config_template
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        bk_username = params.pop("bk_username")
        bk_app_code = params.pop("bk_app_code")

        plugin, created = models.PluginConfigTemplate.objects.update_or_create(
            plugin_name=params["plugin_name"],
            plugin_version=params["plugin_version"],
            name=params["name"],
            version=params["version"],
            defaults=dict(
                plugin_name=params["plugin_name"],
                plugin_version=params["plugin_version"],
                name=params["name"],
                version=params["version"],
                format=params["format"],
                content=params["content"],
                file_path=params["file_path"],
                is_release_version=params["is_release_version"],
                creator=bk_username,
                source_app_code=bk_app_code,
            ),
        )

        params["id"] = plugin.id
        return Response(params)

    @action(detail=False, methods=["POST"], url_path="release_config_template")
    def release_config_template(self, request):
        """
        @api {POST} /plugin/release_config_template/ 发布配置模板
        @apiName release_plugin_config_template
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        bk_username = params.pop("bk_username")
        bk_app_code = params.pop("bk_app_code")

        if "id" in params:
            plugin_templates = models.PluginConfigTemplate.objects.filter(id__in=params["id"])
        else:
            plugin_templates = models.PluginConfigTemplate.objects.filter(**params)

        # 更改发布状态
        plugin_templates.update(is_release_version=True)

        result = []
        for template in plugin_templates:
            result.append(
                dict(
                    id=template.id,
                    plugin_name=template.plugin_name,
                    plugin_version=template.plugin_version,
                    name=template.name,
                    version=template.version,
                    format=template.format,
                    file_path=template.file_path,
                    is_release_version=template.is_release_version,
                    creator=bk_username,
                    content=template.content,
                    source_app_code=bk_app_code,
                )
            )

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="render_config_template")
    def render_config_template(self, request):
        """
        @api {POST} /plugin/render_config_template/ 渲染配置模板
        @apiName render_plugin_config_template
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        bk_username = params.pop("bk_username")
        bk_app_code = params.pop("bk_app_code")
        data = params.pop("data")

        try:
            if "id" in params:
                plugin_template = models.PluginConfigTemplate.objects.get(id=params["id"])
            else:
                plugin_template = models.PluginConfigTemplate.objects.get(**params)
        except models.PluginConfigTemplate.DoesNotExist:
            raise ValidationError("plugin template not found")

        instance = plugin_template.create_instance(data, bk_username, bk_app_code)

        return Response(
            dict(
                id=instance.id,
                md5=instance.data_md5,
                creator=instance.creator,
                source_app_code=instance.source_app_code,
            )
        )

    @action(detail=False, methods=["GET"], url_path="query_config_template")
    def query_config_template(self, request):
        """
        @api {GET} /plugin/query_config_template/ 查询配置模板
        @apiName query_plugin_config_template
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        params.pop("bk_username")
        params.pop("bk_app_code")

        if "id" in params:
            plugin_templates = models.PluginConfigTemplate.objects.filter(id=params["id"])
        else:
            plugin_templates = models.PluginConfigTemplate.objects.filter(**params)

        result = []
        for template in plugin_templates:
            result.append(
                dict(
                    id=template.id,
                    plugin_name=template.plugin_name,
                    plugin_version=template.plugin_version,
                    name=template.name,
                    version=template.version,
                    format=template.format,
                    path=template.file_path,
                    is_release_version=template.is_release_version,
                    creator=template.creator,
                    content=base64.b64encode(template.content),
                    source_app_code=template.source_app_code,
                )
            )

        return Response(result)

    @action(detail=False, methods=["GET"], url_path="query_config_instance")
    def query_config_instance(self, request):
        """
        @api {GET} /plugin/query_config_instance/ 查询配置模板实例
        @apiName query_plugin_config_instance
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        params.pop("bk_username")
        params.pop("bk_app_code")

        if "id" in params:
            plugin_instances = models.PluginConfigInstance.objects.filter(id=params["id"])
        else:
            plugin_templates = models.PluginConfigTemplate.objects.filter(**params)
            plugin_instances = models.PluginConfigInstance.objects.filter(
                plugin_config_template__in=[template.id for template in plugin_templates]
            )

        result = []

        for instance in plugin_instances:
            base64_content = base64.b64encode(instance.content)
            md5_client = hashlib.md5()
            md5_client.update(instance.content)
            md5 = md5_client.hexdigest()

            result.append(
                dict(
                    id=instance.id,
                    content=base64_content,
                    md5=md5,
                    creator=instance.creator,
                    source_app_code=instance.source_app_code,
                )
            )

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="start_debug")
    def start_debug(self, request):
        """
        @api {POST} /plugin/start_debug/ 开始调试
        @apiName start_debug
        @apiGroup backend_plugin
        """
        params = self.get_validated_data()
        host_info = params["host_info"]

        try:
            host = models.Host.objects.get(
                bk_biz_id=host_info["bk_biz_id"], inner_ip=host_info["ip"], bk_cloud_id=host_info["bk_cloud_id"],
            )
        except models.Host.DoesNotExist:
            raise ValidationError("host does not exist")

        plugin_id = params.get("plugin_id")
        try:
            if plugin_id:
                package = models.Packages.objects.get(id=plugin_id)
            else:
                os_type = host.os_type.lower()
                cpu_arch = models.Host.get_cpu_arch_by_os(os_type)
                package = models.Packages.objects.get(
                    project=params["plugin_name"], version=params["version"], os=os_type, cpu_arch=cpu_arch
                )
        except models.Packages.DoesNotExist:
            raise ValidationError("plugin does not exist")

        if not package.is_ready:
            raise ValidationError("plugin is not ready")

        configs = models.PluginConfigInstance.objects.in_bulk(params["config_ids"])

        # 更新控制信息
        debug_root_mapping = {
            "linux": "/tmp/nodeman_debug/",
            "windows": "c:\\tmp\\nodeman_debug",
        }
        debug_root = debug_root_mapping.get(package.os, debug_root_mapping["linux"])
        if package.os == const.PluginOsType.windows:
            path_handler = ntpath
        else:
            path_handler = posixpath
        plugin_dir_name = "{plugin_name}-{version}".format(plugin_name=package.project, version=package.version)
        install_path = path_handler.join(debug_root, plugin_dir_name)

        setup_path = path_handler.join(install_path, "external_plugins", params["plugin_name"])

        control_info = misc.ProcessControlInfoSerializer(instance=package.proc_control).data
        control_info.update(
            install_path=install_path,
            gse_agent_home=env.get_gse_env_path("", package.os == const.PluginOsType.windows)["install_path"],
            setup_path=setup_path,
            pid_path=path_handler.join(setup_path, "pid", "%s.pid" % package.project),
            log_path=path_handler.join(setup_path, "log"),
            data_path=path_handler.join(setup_path, "data"),
        )

        # 更新配置文件信息
        built_in_context = {
            "control_info": control_info,
        }

        # 渲染配置文件
        config_params = []
        for config_id in params["config_ids"]:
            config = configs.get(config_id)
            if not config:
                raise ValidationError("config {} does not exist".format(config_id))
            config_template = config.template
            if config_template.plugin_name != package.project:
                raise ValidationError("config {} does not belong to plugin {}".format(config_id, package.project))
            config_params.append(
                {
                    "content": config.render_config_template(built_in_context),
                    "id": config.id,
                    "render_data": config.render_data,
                    "file_path": config_template.file_path,
                    "name": config_template.name,
                    "version": config_template.version,
                    "template_id": config_template.id,
                    "plugin_name": config_template.plugin_name,
                    "plugin_version": config_template.plugin_version,
                    "is_release_version": config_template.is_release_version,
                }
            )

        host_status = ProcessStatus(
            bk_host_id=host.bk_host_id,
            name=package.project,
            version=package.version,
            configs=config_params,
            setup_path=control_info["setup_path"],
            log_path=control_info["log_path"],
            data_path=control_info["data_path"],
            pid_path=control_info["pid_path"],
            source_type=ProcessStatus.SourceType.DEBUG,
        )
        # get id
        host_status.save()

        plugin_manager = manager.PluginManager(host_status, params["bk_username"])
        pipeline_id = plugin_manager.debug(install_path, script_timeout=60 * 10)

        host_status.source_id = pipeline_id
        host_status.save()
        return Response({"task_id": pipeline_id})

    @action(detail=False, methods=["POST"], url_path="stop_debug")
    def stop_debug(self, request):
        """
        @api {POST} /plugin/stop_debug/ 停止调试
        @apiName stop_debug
        @apiGroup backend_plugin
        """
        pipeline_id = request.data["task_id"]
        # 寻找这个任务对应的PipelineTree
        try:
            pipeline = models.PipelineTree.objects.get(id=pipeline_id)
        except models.PipelineTree.DoesNotExist:
            logger.error("user try to query PipelineTree->[%s] but is not exists." % pipeline_id)
            raise JobNotExistError(_("找不到请求的任务，请确认后重试"))

        result, message = manager.PluginManager.stop_debug(pipeline)
        if not result:
            raise StopDebugError(message)

        return Response()

    @action(detail=False, methods=["GET"], url_path="query_debug")
    def query_debug(self, request):
        """
        @api {GET} /plugin/query_debug/ 查询调试结果
        @apiName query_debug
        @apiGroup backend_plugin
        """
        pipeline_id = request.query_params["task_id"]

        # 寻找这个任务对应的PipelineTree
        try:
            pipeline = models.PipelineTree.objects.get(id=pipeline_id)
        except models.PipelineTree.DoesNotExist:
            logger.error("user try to query PipelineTree->[%s] but is not exists." % pipeline_id)
            raise JobNotExistError(_("找不到请求的任务，请确认后重试"))

        log_content, status, step = manager.PluginManager.get_debug_status(pipeline)
        return Response({"status": status, "step": step, "message": "\n".join(log_content)})

    @action(detail=False, methods=["POST"])
    def create_export_task(self, request):
        """
        @api {POST} /plugin/create_export_task/ 触发插件打包导出
        @apiName create_export_plugin_task
        @apiGroup backend_plugin
        """

        params = self.get_validated_data()

        record = models.DownloadRecord.create_record(
            category=params["category"],
            query_params=params["query_params"],
            creator=params["creator"],
            source_app_code=params["bk_app_code"],
        )
        logger.info(
            "user->[%s] request to export from system->[%s] success created record->[%s]."
            % (params["creator"], params["bk_app_code"], record.id)
        )

        tasks.export_plugin.delay(record.id)
        logger.info("record->[%s] now is active to celery" % record.id)

        return Response({"job_id": record.id})

    @action(detail=False, methods=["GET"])
    def query_export_task(self, request):
        """
        @api {GET} /plugin/query_export_task/ 获取一个导出任务结果
        @apiName query_export_plugin_task
        @apiGroup backend_plugin
        """
        # 及时如果拿到None的job_id，也可以通过DB查询进行防御
        job_id = request.GET.get("job_id")

        try:
            record = models.DownloadRecord.objects.get(id=job_id)
        except models.DownloadRecord.DoesNotExist:
            logger.error("record->[%s] not exists, something go wrong?" % job_id)
            raise ValueError(_("请求任务不存在，请确认后重试"))

        uri = settings.BACKEND_HOST + "/backend/export/download/"
        uri_with_params = "?".join([uri, record.download_params])

        response_data = {
            "is_finish": record.is_finish,
            "is_failed": record.is_failed,
            "download_url": uri_with_params if not record.is_failed else "",  # 下载URL
            "error_message": record.error_message,
        }

        logger.info("export record->[{}] response_data->[{}]".format(job_id, response_data))
        return Response(response_data)


@csrf_exempt
@login_exempt
def upload_package(request):
    """
    @api {POST} /package/upload/ 上传文件接口
    @apiName upload_file
    @apiGroup backend_plugin
    """
    # 1. 获取上传的参数 & nginx的上传信息
    ser = UploadInfoSerializer(data=request.POST)
    if not ser.is_valid():
        logger.error("failed to valid request data for->[%s] maybe something go wrong?" % ser.errors)
        raise ValueError(_("请求参数异常，请确认后重试"))

    # 2. 判断哈希及参数是否符合预期
    file_local_md5 = ser.data["file_local_md5"]
    file_name = ser.data["file_name"]
    md5 = ser.data["md5"]

    if file_local_md5 != md5:
        logger.error("failed to valid file md5 local->[{}] user->[{}] maybe network error".format(file_local_md5, md5))
        raise ValueError(_("上传文件MD5校验失败，请确认重试"))

    # 3. 创建上传的记录
    record = models.UploadPackage.create_record(
        module=ser.data["module"],
        file_path=ser.data["file_local_path"],
        md5=md5,
        operator=ser.data["bk_username"],
        source_app_code=ser.data["bk_app_code"],
        file_name=file_name,
    )
    logger.info(
        "user->[%s] from app->[%s] upload file->[%s] success."
        % (record.creator, record.source_app_code, record.file_path)
    )
    return JsonResponse(
        {
            "result": True,
            "message": "",
            "code": "00",
            "data": {
                "id": record.id,  # 包文件的ID
                "name": record.file_name,  # 包名
                "pkg_size": record.file_size,  # 单位byte
            },
        }
    )


@csrf_exempt
@login_exempt
def export_download(request):
    """
    下载导出的内容，此处不做实际的文件读取，将由nginx负责处理
    :param request: 具有参数：id(下载记录ID)， key(校验参数)
    :return:
    """
    """
    @api {GET} /export/download/ 下载导出的内容,此处不做实际的文件读取，将由nginx负责处理
    @apiName download_content
    @apiGroup backend_plugin
    """

    # 及时如果拿到None的job_id，也可以通过DB查询进行防御
    job_id = request.GET.get("job_id")
    key = request.GET.get("key")

    try:
        record = models.DownloadRecord.objects.get(id=job_id)

    except models.DownloadRecord.DoesNotExist:
        logger.error("record->[%s] not exists, something go wrong?" % job_id)
        raise ValueError(_("请求任务不存在，请确认后重试"))

    if not record.download_key == key:
        logger.error(
            "try to download record->[%s] but request_key->[%s] is not match target_key->[%s]"
            % (job_id, key, record.download_key)
        )
        return HttpResponseForbidden(_("下载安全校验失败"))

    filename = os.path.basename(record.file_path)
    response = JsonResponse({"result": True, "message": "", "code": "00", "data": None})
    # 增加实际的下载文件名字准备
    request_str = six.moves.urllib.parse.urlencode({"real_name": os.path.basename(record.file_path).encode("utf8")})
    uri = os.path.join("/protect_download", filename)

    redirect_url = "?".join([uri, request_str])
    response["X-Accel-Redirect"] = redirect_url

    return response
