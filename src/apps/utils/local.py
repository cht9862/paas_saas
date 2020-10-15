# -*- coding: utf-8 -*-
"""
记录线程变量
"""
import uuid
from threading import local

from apps.exceptions import BaseException

_local = local()


def activate_request(request, request_id=None):
    """
    激活request线程变量
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    request.request_id = request_id
    _local.request = request
    return request


def get_request():
    """
    获取线程请求request
    """
    try:
        return _local.request
    except AttributeError:
        raise BaseException("request thread error!")


def get_request_id():
    """
    获取request_id
    """
    try:
        return get_request().request_id
    except BaseException:
        return str(uuid.uuid4())


def get_request_username():
    """
    获取请求的用户名
    """
    try:
        return get_request().user.username
    except Exception:
        return ""


def get_request_app_code():
    """
    获取线程请求中的 APP_CODE，非线程请求返回空字符串
    """
    try:
        return _local.bk_app_code
    except AttributeError:
        return ""


def set_local_param(key, value):
    """
    设置自定义线程变量
    """
    setattr(_local, key, value)


def del_local_param(key):
    """
    删除自定义线程变量
    """
    if hasattr(_local, key):
        delattr(_local, key)


def get_local_param(key, default=None):
    """
    获取线程变量
    """
    return getattr(_local, key, default)
