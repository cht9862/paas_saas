# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.core.management.base import BaseCommand
from django.http import HttpRequest
from rest_framework.request import Request

from apps.backend.subscription.views import SubscriptionViewSet
from apps.node_man.models import SubscriptionStep, Subscription, ProcessStatus


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        重跑存量的插件订阅任务
        """
        plugin_subscription_ids = SubscriptionStep.objects.filter(type="PLUGIN").values_list(
            "subscription_id", flat=True
        )
        valid_subscriptions = Subscription.objects.filter(
            id__in=set(plugin_subscription_ids), enable=True, is_deleted=False
        )
        count = valid_subscriptions.count()
        # 首先把现有的任务终止掉
        for index, subscription in enumerate(valid_subscriptions):
            print("Start revoking {}/{} subscription, id: {}".format(index + 1, count, subscription.id))
            http_request = HttpRequest()
            http_request._body = json.dumps(
                {"subscription_id": subscription.id, "bk_username": "admin", "bk_app_code": "bk_nodeman"}
            )
            drf_request = Request(http_request)
            try:
                SubscriptionViewSet(request=drf_request, action="revoke", format_kwarg=None).revoke(drf_request)
            except Exception:
                continue
            print("End revoking {}/{} subscription, id: {}".format(index + 1, count, subscription.id))

        # 清理ProcessStatus表
        # 再重新执行一遍订阅
        for index, subscription in enumerate(valid_subscriptions):
            print("Start retrying {}/{} subscription, id: {}".format(index + 1, count, subscription.id))
            ProcessStatus.objects.filter(source_id=subscription.id).delete()
            http_request = HttpRequest()
            http_request._body = json.dumps(
                {"subscription_id": subscription.id, "bk_username": "admin", "bk_app_code": "bk_nodeman"}
            )
            drf_request = Request(http_request)
            try:
                SubscriptionViewSet(request=drf_request, action="run", format_kwarg=None).run(drf_request)
            except Exception:
                continue
            print("End retrying {}/{} subscription, id: {}".format(index + 1, count, subscription.id))
