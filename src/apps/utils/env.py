# -*- coding: utf-8 -*-
"""
该工具用户获取环境变量相关的内容
"""

import logging
import os

from django.conf import settings

logger = logging.getLogger("app")


def get_env_list(env_prefix):
    """
    获取可以遍历的环境变量信息，并通过一个数组的方式返回
    例如，获取IP0 ~ IPn环境变量, 调用get_env_list(env_prefix="IP"), 返回["x.x.x.x", "x.x.x.x"]
    :param env_prefix: 环境变量前缀
    :return: ["info", "info"]
    """
    index = 0
    result = []
    while True:
        current_name = f"{env_prefix}{index}"
        current_value = os.getenv(current_name)

        # 此轮已经不能再获取新的变量了，可以返回
        # 此处，我们相信变量不存在跳跃的情况
        if current_value is None:
            break

        result.append(current_value)
        index += 1

    logger.info(f"env->[{env_prefix}] got total env count->[{index}]")
    return result


def get_gse_env_path(package_name, is_windows=False):
    """
    获取gse agent的路径信息
    :param package_name: 插件名，因为部分文件配置路径与插件名有关
    :param is_windows: 是否windows环境下的配置
    :return: {
        "install_path": "/usr/local",
        "log_path": "/usr/local",
        "pid_path": "/usr/local",
        "data_path": "/usr/local",
    }
    """
    # windows系统下的路径配置
    if is_windows:
        return {
            "install_path": settings.GSE_WIN_AGENT_HOME,
            "log_path": settings.GSE_WIN_AGENT_LOG_DIR,
            "pid_path": settings.GSE_WIN_AGENT_RUN_DIR + "\\" + package_name + ".pid",
            "data_path": settings.GSE_WIN_AGENT_DATA_DIR,
        }
    # linux & aix系统下的配置
    else:
        return {
            "install_path": settings.GSE_AGENT_HOME,
            "log_path": settings.GSE_AGENT_LOG_DIR,
            "pid_path": settings.GSE_AGENT_RUN_DIR + "/" + package_name + ".pid",
            "data_path": settings.GSE_AGENT_DATA_DIR,
        }
