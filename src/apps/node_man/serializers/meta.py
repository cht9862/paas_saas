# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from apps.node_man.constants import JOB_MAX_VALUE, NODE_MAN_LOG_LEVEL


class JobSettingSerializer(serializers.Serializer):
    """
    用于创建任务配置的验证
    """

    install_p_agent_timeout = serializers.IntegerField(label=_("安装P-Agent超时时间"), max_value=JOB_MAX_VALUE, min_value=0)
    install_agent_timeout = serializers.IntegerField(label=_("安装Agent超时时间"), max_value=JOB_MAX_VALUE, min_value=0)
    install_proxy_timeout = serializers.IntegerField(label=_("安装Proxy超时时间"), max_value=JOB_MAX_VALUE, min_value=0)
    install_download_limit_speed = serializers.IntegerField(label=_("安装下载限速"), max_value=JOB_MAX_VALUE, min_value=0)
    parallel_install_number = serializers.IntegerField(label=_("并行安装数"), max_value=JOB_MAX_VALUE, min_value=0)
    node_man_log_level = serializers.ChoiceField(label=_("节点管理日志级别"), choices=list(NODE_MAN_LOG_LEVEL))
