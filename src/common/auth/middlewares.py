# -*- coding: utf-8 -*-
import ujson as json
from django.http import JsonResponse
from django.middleware.common import MiddlewareMixin

from common.log import logger
from apps.utils.local import set_local_param, get_local_param

from .identities import (UserIdentity, extract_value)
from .exceptions import BaseAuthError, AuthenticateError


def _convert_exception_to_response(exc):
    """
    将权限模块的异常输出转换为标准响应

    @param {BaseAuthError} exc
    """
    return JsonResponse({
        'result': False,
        'message': exc.message,
        'data': None,
        'code': exc.code,
        'errors': None
    })


class AuthenticationMiddleware(MiddlewareMixin):
    """
    身份认证器：暂时只支持User
    """
    IdentityBackends = [UserIdentity]

    @classmethod
    def match_backend(cls, authentication_method):
        for backend in cls.IdentityBackends:
            if backend.NAME == authentication_method:
                return backend

    def process_request(self, request):
        authentication_method = 'user'
        identity = None
        try:
            backend = self.match_backend(authentication_method)
            if backend:
                ret = backend.authenticate(request)
                if ret is not None:
                    identity = ret

            if identity is None:
                logger.error('[No Identity] authentication method does not match')
                raise AuthenticateError()
        except BaseAuthError as e:
            return _convert_exception_to_response(e)

        set_local_param('identity', identity)

        bk_username = identity.bk_username
        bk_app_code = identity.bk_app_code

        # 为了兼容框架中从 local 文件中获取当前访问的 APP_CODE 和 USERNAME
        set_local_param('bk_username', bk_username)
        set_local_param('bk_app_code', bk_app_code)

        # 认证信息，用于直接透传给esb
        try:
            auth_info = json.loads(extract_value(request, 'auth_info'))
        except (ValueError, TypeError):
            auth_info = {}

        set_local_param('auth_info', auth_info)

        return None


def get_identity():
    """
    获取当前访问的身份
    """
    return get_local_param('identity')


def get_request_username():
    """
    获取当前访问身份的用户名
    """
    return get_identity().bk_username


def get_request_app_code():
    """
    获取当前访问身份的APP
    """
    return get_identity().bk_app_code
