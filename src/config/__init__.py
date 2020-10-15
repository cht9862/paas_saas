# -*- coding: utf-8 -*-

import os
import importlib

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2019 Tencent BlueKing. All Rights Reserved."
__all__ = ['celery_app', 'ENVIRONMENT', 'RUN_VER', 'APP_CODE', 'SECRET_KEY', 'BK_URL', 'BASE_DIR']

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

# app 基本信息

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {
        'development': 'dev',
        'testing': 'stag',
        'production': 'prod',
    }.get(PAAS_V2_ENVIRONMENT)

# SaaS运行版本，如非必要请勿修改
RUN_VER = os.environ.get('BKPAAS_ENGINE_REGION', 'open')
conf_module = "sites.{}.config".format(RUN_VER)
_module = importlib.import_module(conf_module)

# 蓝鲸平台URL
BK_URL = os.getenv('BKPAAS_URL', None)  # noqa

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))


DB_NAME_VARIABLE = os.environ.get('DB_NAME_VARIABLE', 'DB_NAME')
DB_USERNAME_VARIABLE = os.environ.get('DB_USERNAME_VARIABLE', 'DB_USERNAME')
DB_PASSWORD_VARIABLE = os.environ.get('DB_PASSWORD_VARIABLE', 'DB_PASSWORD')
DB_HOST_VARIABLE = os.environ.get('DB_HOST_VARIABLE', 'DB_HOST')
DB_PORT_VARIABLE = os.environ.get('DB_PORT_VARIABLE', 'DB_PORT')
