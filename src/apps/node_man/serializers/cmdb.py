# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from apps.node_man.constants import IamActionType


class BizSerializer(serializers.Serializer):
    """
    用于云区域列表校验
    """

    action = serializers.ChoiceField(
        label=_("操作"),
        required=True,
        choices=[
            IamActionType.task_history_view,
            IamActionType.agent_view,
            IamActionType.agent_operate,
            IamActionType.proxy_operate,
            IamActionType.plugin_view,
            IamActionType.plugin_operate,
        ],
    )
