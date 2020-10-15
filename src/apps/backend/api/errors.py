# -*- coding: utf-8 -*-


from django.utils.translation import gettext_lazy as _

from apps.exceptions import BaseException


class EmptyResponseError(BaseException):
    """ 无响应 """

    code = 3801000
    name = _("无响应")
    message_tpl = _("API({api_name})没有返回响应")


class FalseResultError(BaseException):
    """ 接口调用错误 """

    code = 3801001
    name = _("接口调用错误")
    message_tpl = _("API({api_name})调用出错：{error_message}")


class JobPollTimeout(BaseException):
    """ Job轮询超时 """

    code = 3801002
    name = _("Job轮询超时")
    message_tpl = _("Job任务({job_instance_id})轮询超时")


class GsePollTimeout(BaseException):
    """ GSE轮询超时 """

    code = 3801004
    name = _("GSE轮询超时")
    message_tpl = _("GSE任务({task_id})轮询超时")
