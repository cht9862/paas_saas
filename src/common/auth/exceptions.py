# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from apps.exceptions import ErrorCode, BaseException


class BaseAuthError(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_AUTH
    MESSAGE = "权限基类"


class PermissionDeniedError(BaseAuthError):
    ERROR_CODE = '001'
    MESSAGE = _("权限不足")


class ParamMissError(BaseAuthError):
    ERROR_CODE = '002'
    MESSAGE = _("必要参数缺失")


class AuthenticateError(BaseAuthError):
    ERROR_CODE = '003'
    MESSAGE = _("认证不通过，请提供合法的 BKData 认证信息")


class InvalidSecretError(BaseAuthError):
    ERROR_CODE = '004'
    MESSAGE = _("内部模块调用请传递准确的 bk_app_code 和 bk_app_secret")


class InvalidTokenError(BaseAuthError):
    ERROR_CODE = '005'
    MESSAGE = _("请传递合法的 data_token")


class NotWhiteAppCallError(BaseAuthError):
    ERROR_CODE = '006'
    MESSAGE = _("非白名单 APP 不可直接访问接口")


class NoIdentityError(BaseAuthError):
    ERROR_CODE = '007'
    MESSAGE = _("未检测到有效的认证信息")


class GroupDoesNotExists(BaseAuthError):
    ERROR_CODE = '008'
    MESSAGE = _("用户组不存在")


class GroupIdDoesNotExists(BaseAuthError):
    ERROR_CODE = '009'
    MESSAGE = _("参数异常：用户组ID不存在")
