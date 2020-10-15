# -*- coding: utf-8 -*-
import ujson as json
from .exceptions import (AuthenticateError)


def extract_parmas(request):
    """
    根据请求类型，提取请求参数
    @return {Dict} 字典
    """
    if request.method == 'GET':
        return request.GET

    # 请求方法 POST，需要兼容各种旧版请求方式
    elif request.method == 'POST':
        # 优先使用 application/json 解析
        try:
            return json.loads(request.body)
        except ValueError:
            pass

        # 其次使用 application/form-data 解析
        try:
            return request.POST.dict()
        except Exception:
            pass

    # 请求方法 PUT、PATCH、DELETE 从 body 中获取参数内容，并且仅支持 json 格式
    else:
        try:
            return json.loads(request.body)
        except ValueError:
            pass

    # 避免data为None的情况导致返回的数据结构不一致
    return {}


def extract_value(request, key):
    params = extract_parmas(request)

    if key in params:
        return params[key]

    return ''


class Identity(object):
    NAME = ''

    def __init__(self, bk_app_code, bk_username):
        self.bk_app_code = bk_app_code
        self.bk_username = bk_username

    @classmethod
    def authenticate(cls, request):
        """
        校验来自外部的接口是否合法，是否符合认证要求
        """
        raise NotImplementedError


class UserIdentity(Identity):
    NAME = 'user'

    @classmethod
    def authenticate(cls, request):
        bk_app_code = extract_value(request, 'bk_app_code')
        bk_username = request.user.username

        if not bk_username:
            raise AuthenticateError()

        return cls(bk_app_code, bk_username)
