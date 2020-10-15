# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import BaseException


class BackendBaseException(BaseException):
    MODULE_CODE = 2000


class UploadPackageNotExistError(BackendBaseException):
    MESSAGE = _("文件包不存在")
    ERROR_CODE = 1


class JobNotExistError(BackendBaseException):
    MESSAGE = _("任务不存在")
    ERROR_CODE = 2


class StopDebugError(BackendBaseException):
    MESSAGE = _("停止调试失败")
    ERROR_CODE = 3
