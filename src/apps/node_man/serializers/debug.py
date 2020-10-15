# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class SubscriptionDebugSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField(label=_("订阅任务ID"), required=True)


class TaskDebugSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField(label=_("订阅任务ID"), required=True)
    task_id = serializers.IntegerField(label=_("任务ID"), required=True)


class HostDebugSerializer(serializers.Serializer):
    bk_host_id = serializers.IntegerField(label=_("主机ID"), required=True)
