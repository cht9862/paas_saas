# -*- coding: utf-8 -*-
"""
context_processor for common(setting)

除setting外的其他context_processor内容，均采用组件的方式(string)
"""
from django.utils.translation import ugettext as _
from django.conf import settings
import datetime

from blueapps.account.conf import ConfFixture
from apps.node_man.handlers.iam import IamHandler
from apps.utils.local import get_request_username
from apps.node_man import constants


def mysetting(request):
    return {
        "gettext": _,
        "_": _,
        "LANGUAGES": settings.LANGUAGES,
        # 基础信息
        "RUN_MODE": settings.RUN_MODE,
        "ENVIRONMENT": settings.ENVIRONMENT,
        "APP_CODE": settings.APP_CODE,
        "SITE_URL": settings.SITE_URL,
        "RUN_VER_DISPLAY": settings.RUN_VER_DISPLAY,
        # 远程静态资源url
        "REMOTE_STATIC_URL": settings.REMOTE_STATIC_URL,
        # 静态资源
        "STATIC_URL": settings.STATIC_URL,
        "BK_STATIC_URL": settings.STATIC_URL[: len(settings.STATIC_URL) - 1],
        "STATIC_VERSION": settings.STATIC_VERSION,
        # 登录跳转链接
        "LOGIN_URL": ConfFixture.LOGIN_URL,
        "LOGIN_SERVICE_URL": ConfFixture.LOGIN_URL,
        # PAAS域名
        "BK_PAAS_HOST": settings.BK_PAAS_HOST,
        # 当前页面，主要为了login_required做跳转用
        "APP_PATH": request.get_full_path(),
        "NOW": datetime.datetime.now(),
        "RUN_VER": settings.RUN_VER,
        "WEB_TITLE": _("节点管理 | 蓝鲸"),
        "DEFAULT_CLOUD": constants.DEFAULT_CLOUD,
        "USERNAME": request.user.username,
        # 是否使用权限中心
        "USE_IAM": settings.USE_IAM,
        # 如果是权限中心，使用权限中心的全局配置权限
        # 如果不是权限中心，使用超管权限
        "GLOBAL_SETTING_PERMISSION": IamHandler.iam_global_settings_permission(get_request_username()),
        # 任务配置权限
        "GLOBAL_TASK_CONFIG_PERMISSION": IamHandler.globe_task_config(get_request_username()),
        "GSE_LISTEN_PORT": "48668,58625,58925,10020-10030",
        "PROXY_LISTEN_PORT": "58930,10020-10030",
        "WXWORK_UIN": getattr(settings, "WXWORK_UIN", ""),
        "DESTOP_URL": getattr(settings, "DESTOP_URL", ""),
        # 默认端口
        "DEFAULT_SSH_PORT": getattr(settings, "BKAPP_DEFAULT_SSH_PORT", 22),
        "USE_TJJ": getattr(settings, "USE_TJJ", False),
    }
