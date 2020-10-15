# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from apps.node_man import constants as const
from apps.node_man.models import SubscriptionInstanceRecord
from common.log import logger


def update_subscription_instance_record(task_id, count=1):
    logger.info(f"{task_id} | clean_subscription_record_info: Start of cleaning up subscription records.[{count}]")
    record_query_set = SubscriptionInstanceRecord.objects.filter(
        update_time__lte=timezone.now() - timezone.timedelta(days=1), need_clean=True
    )[0 : const.QUERY_EXPIRED_INFO_LENS]

    # 结束递归
    if not record_query_set:
        return

    for record in record_query_set:
        if isinstance(record.instance_info, dict):
            try:
                if record.instance_info["host"].get("password"):
                    record.instance_info["host"]["password"] = ""
                if record.instance_info["host"].get("key"):
                    record.instance_info["host"]["key"] = ""
            except (KeyError, TypeError):
                pass
            record.need_clean = False
            record.save()

    update_subscription_instance_record(task_id, count + 1)


@periodic_task(
    queue="default",
    options={"queue": "default"},
    run_every=crontab(hour="*", minute="*/15", day_of_week="*", day_of_month="*", month_of_year="*"),
)
def clean_subscription_record_info():
    # 清除订阅记录中过期的密码信息
    task_id = clean_subscription_record_info.request.id
    logger.info(f"{task_id} | Start cleaning up subscription records.")
    update_subscription_instance_record(task_id)
    logger.info(f"{task_id} | Clean up subscription records complete.")
