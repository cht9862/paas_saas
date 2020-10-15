# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task

from apps.node_man.policy.tencent_vpc_client import VpcClient
from apps.node_man.models import Host
from apps.node_man.exceptions import ConfigurationPolicyError
from apps.node_man.constants import NodeType
from common.log import logger


@periodic_task(
    queue="default",
    options={"queue": "default"},
    run_every=crontab(hour="*", minute="*/1", day_of_week="*", day_of_month="*", month_of_year="*"),
)
def configuration_policy():
    """
    出海开通策略任务此任务与ConfigurationPolicy原子强绑定，不在常规企业版内启动
    """
    task_id = configuration_policy.request.id
    logger.info(f"{task_id} | Start configuring policy.")

    client = VpcClient()
    is_ok, message = client.init()
    if not is_ok:
        logger.error(f"configuration_policy error: {message}")
        raise ConfigurationPolicyError()

    # 兼容nat网络，外网IP和登录IP都添加到策略中
    hosts = Host.objects.filter(node_type=NodeType.PROXY).values("login_ip", "outer_ip")
    need_add_ip_list = []
    for host in hosts:
        need_add_ip_list.append(host["login_ip"])
        need_add_ip_list.append(host["outer_ip"])

    for template in client.ip_templates:
        using_ip_list = client.describe_address_templates(template)
        need_add_ip_list = list(set(need_add_ip_list) - set(using_ip_list))
        if need_add_ip_list:
            new_ip_list = need_add_ip_list + using_ip_list
            is_ok, message = client.add_ip_to_template(template, new_ip_list, need_query=False)
            if not is_ok:
                logger.error(f"configuration_policy error: {message}")
                raise ConfigurationPolicyError()

    logger.info(f"{task_id} | Configuration policy complete.")
