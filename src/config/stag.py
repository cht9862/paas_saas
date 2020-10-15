# -*- coding: utf-8 -*-
import os
import importlib

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 预发布环境
RUN_MODE = "STAGING"

# 对日志级别进行配置，可以在这里修改
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# allow all hosts
CORS_ORIGIN_ALLOW_ALL = True

# cookies will be allowed to be included in cross-site HTTP requests
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE += ("corsheaders.middleware.CorsMiddleware",)

# 加载各个版本特殊配置
try:
    conf_module = "sites.{run_ver}.config.stag".format(run_ver=RUN_VER)
    _module = importlib.import_module(conf_module)
    for _setting in dir(_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(_module, _setting)
except ImportError:
    pass
