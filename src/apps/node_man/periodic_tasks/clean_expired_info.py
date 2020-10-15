# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from apps.node_man import constants as const
from apps.node_man.models import IdentityData
from common.log import logger


def clean_identity_data(task_id, start, end):
    identity_bk_host_ids = (
        IdentityData.objects.filter(retention=1, updated_at__lte=timezone.now() - timezone.timedelta(days=1))
        .exclude(key=None, password=None, extra_data=None)
        .values_list(flat=True)[start:end]
    )
    if not identity_bk_host_ids:
        # 结束递归
        return

    logger.info(
        f"{task_id} | "
        f"Clean up the host authentication information with a retention period of one day.[{start}-{end}]"
    )
    IdentityData.objects.filter(bk_host_id__in=list(identity_bk_host_ids)).update(
        key=None, password=None, extra_data=None
    )
    clean_identity_data(task_id, end, end + const.QUERY_EXPIRED_INFO_LENS)


@periodic_task(
    queue="default",
    options={"queue": "default"},
    run_every=crontab(hour="*/6", minute="0", day_of_week="*", day_of_month="*", month_of_year="*"),
)
def clean_expired_info():
    """
    清理保留期限为一天的主机认证信息
    """
    # 清除过期的账户信息
    task_id = clean_expired_info.request.id
    logger.info(f"{task_id} | Start cleaning host authentication information.")
    clean_identity_data(task_id, 0, const.QUERY_EXPIRED_INFO_LENS)
    logger.info(f"{task_id} | Clean up the host authentication information complete.")
