# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from celery.schedules import crontab
from celery.task import periodic_task

from common.api.models import DataAPIRecord


@periodic_task(run_every=crontab(minute='0', hour='0'))
def delete_api_log():
    """
    每天清理dataapi日志
    """
    # 清理一周前的日志
    how_many_days = 7
    DataAPIRecord.objects.filter(request_datetime__lte=datetime.now() - timedelta(days=how_many_days)).delete()
