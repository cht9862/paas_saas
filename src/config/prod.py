# -*- coding: utf-8 -*-
import importlib
import os

from config import RUN_VER


if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 正式环境
RUN_MODE = "PRODUCT"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")


# 加载各个版本特殊配置
try:
    conf_module = "sites.{run_ver}.config.prod".format(run_ver=RUN_VER)
    _module = importlib.import_module(conf_module)
    for _setting in dir(_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(_module, _setting)
except ImportError:
    pass


if os.environ.get("BK_BACKEND_CONFIG", None) is not None:
    # 后台部署
    FORCE_SCRIPT_NAME = ""
    BK_LOG_DIR = os.getenv("BK_LOG_DIR", "/data/bkee/logs/bknodeman/")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",  # 默认用mysql
            "NAME": os.getenv("BK_NODEMAN_MYSQL_NAME", "bk_nodeman"),  # 数据库名
            "USER": os.getenv("BK_NODEMAN_MYSQL_USER"),
            "PASSWORD": os.getenv("BK_NODEMAN_MYSQL_PASSWORD"),
            "HOST": os.getenv("BK_NODEMAN_MYSQL_HOST"),
            "PORT": os.getenv("BK_NODEMAN_MYSQL_PORT"),
            "OPTIONS": {"isolation_level": "repeatable read"},
        }
    }
