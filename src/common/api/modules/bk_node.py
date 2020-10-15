# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from common.api.base import DataAPI
from common.api.modules.utils import add_esb_info_before_request
from config.domains import BK_NODE_APIGATEWAY_ROOT


class _BKNodeApi(object):
    MODULE = _("节点管理")

    def __init__(self):

        self.create_subscription = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/create/",
            module=self.MODULE,
            description=u"创建订阅配置",
            before_request=add_esb_info_before_request,
        )
        self.get_subscription_task_status = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/task_result/",
            module=self.MODULE,
            description=u"查看订阅任务运行状态",
            before_request=add_esb_info_before_request,
        )
        self.collect_subscription_task_detail = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/collect_task_result_detail/",
            module=self.MODULE,
            description=u"采集订阅任务中实例的详细状态",
            before_request=add_esb_info_before_request,
        )
        self.get_subscription_task_detail = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/task_result_detail/",
            module=self.MODULE,
            description=u"查询订阅任务中实例的详细状态",
            before_request=add_esb_info_before_request,
        )
        self.run_subscription_task = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/run/",
            module=self.MODULE,
            description=u"执行订阅下发任务",
            before_request=add_esb_info_before_request,
        )
        self.retry_subscription_task = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/retry/",
            module=self.MODULE,
            description=u"重试任务",
            before_request=add_esb_info_before_request,
        )
        self.revoke_subscription_task = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/revoke/",
            module=self.MODULE,
            description=u"终止正在执行的订阅任务",
            before_request=add_esb_info_before_request,
        )
        self.fetch_commands = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/fetch_commands/",
            module=self.MODULE,
            description=u"获取安装命令",
            before_request=add_esb_info_before_request,
        )
        self.retry_node = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/retry_node/",
            module=self.MODULE,
            description=u"原子粒度重试任务",
            before_request=add_esb_info_before_request,
        )
