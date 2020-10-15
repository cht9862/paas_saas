# -*- coding: utf-8 -*-
import datetime

from celery.schedules import crontab
from celery.task import periodic_task

from requests_tracker.models import Record
from common.log import logger


@periodic_task(
    queue="default",
    options={"queue": "default"},
    run_every=crontab(hour="*/3", minute="*", day_of_week="*", day_of_month="*", month_of_year="*"),
)
def clean_requests_tracker_records():
    # 检查组件请求记录，清空2天前的记录
    logger.info("Start cleaning up requests tracker records.")
    two_days_before = datetime.datetime.now() - datetime.timedelta(days=2)
    try:
        Record.objects.filter(date_created__lte=two_days_before,).order_by("id").delete()
    except Exception as e:
        logger.error("Clean record data error: {}".format(e))
    logger.info("Clean up requests tracker records complete.")
