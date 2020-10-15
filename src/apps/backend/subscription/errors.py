# -*- coding: utf-8 -*-


from django.utils.translation import gettext_lazy as _

from apps.exceptions import BaseException


class SubscriptionError(BaseException):
    pass


class SubscriptionNotExist(BaseException):
    """ 订阅不存在 """

    ERROR_CODE = 3810001
    MESSAGE = _("订阅不存在")
    MESSAGE_TPL = _("订阅({subscription_id})不存在")


class ActionCanNotBeNone(BaseException):
    """ 主动触发订阅，当scope存在时，action不能为空 """

    ERROR_CODE = 3810002
    MESSAGE = _("Actions不能为None")
    MESSAGE_TPL = _("当scope存在时，actions不能空")


class SubscriptionTaskNotExist(BaseException):
    """ 订阅任务不存在 """

    ERROR_CODE = 3810003
    MESSAGE = _("订阅任务不存在")
    MESSAGE_TPL = _("订阅任务({task_id})不存在")


class InstanceTaskIsRunning(BaseException):
    """ 实例有执行中任务 """

    ERROR_CODE = 3810003
    MESSAGE = _("实例存在运行中任务")
    MESSAGE_TPL = _("实例存在运行中任务，避免重复下发")


class ConfigRenderFailed(BaseException):
    """ 实例有执行中任务 """

    ERROR_CODE = 3810004
    MESSAGE = _("配置文件渲染失败")
    MESSAGE_TPL = _("配置文件[{name}]渲染失败，原因：{msg}")


class PipelineExecuteFailed(BaseException):
    """ pipeline 执行失败 """

    ERROR_CODE = 3810005
    MESSAGE = _("Pipeline任务执行失败")
    MESSAGE_TPL = _("Pipeline任务执行失败，原因：{msg}")


class PipelineTreeParseError(BaseException):
    """ pipeline 任务树解析失败 """

    ERROR_CODE = 3810006
    MESSAGE = _("Pipeline任务树解析失败")
    MESSAGE_TPL = _("Pipeline任务树解析失败")


class SubscriptionInstanceRecordNotExist(BaseException):
    """ 订阅实例记录不存在 """

    ERROR_CODE = 3810007
    MESSAGE = _("订阅任务实例不存在")
    MESSAGE_TPL = _("订阅任务实例不存在")


class PipelineDuplicateExecution(BaseException):
    """ pipeline 执行失败 """

    ERROR_CODE = 3810008
    MESSAGE = _("Pipeline任务重复执行")
    MESSAGE_TPL = _("Pipeline任务已经开始执行，不能重复执行")


class SubscriptionInstanceEmpty(BaseException):
    """ 订阅实例记录为空 """

    ERROR_CODE = 3810009
    MESSAGE = _("订阅任务实例为空")
    MESSAGE_TPL = _("订阅任务实例为空，不再创建订阅任务")


class PluginValidationError(BaseException):
    """ 插件校验错误 """

    ERROR_CODE = 3810010
    MESSAGE = _("插件校验错误")
    MESSAGE_TPL = _("{msg}")
