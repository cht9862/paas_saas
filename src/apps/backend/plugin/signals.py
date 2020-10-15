# -*- coding: utf-8 -*-
from django.db.models import F

from apps.backend.subscription.tools import create_group_id
from common.log import logger
from apps.node_man.models import SubscriptionInstanceRecord, ProcessStatus


def activity_failed_handler(pipeline_id, *args, **kwargs):
    # 插件部署失败后，重试次数 +1
    instance_record = SubscriptionInstanceRecord.objects.get(pipeline_id=pipeline_id)
    group_id = create_group_id(instance_record.subscription, instance_record.instance_info)
    ProcessStatus.objects.filter(
        source_type=ProcessStatus.SourceType.SUBSCRIPTION, source_id=instance_record.subscription_id, group_id=group_id
    ).update(retry_times=F("retry_times") + 1)
    logger.error("[activity failed] {},{}".format(instance_record.subscription_id, group_id))
