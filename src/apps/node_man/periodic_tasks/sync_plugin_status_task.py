# -*- coding: utf-8 -*-
import re

from celery.schedules import crontab
from celery.task import periodic_task

from apps.component.esbclient import client_v2
from apps.node_man import constants as const
from apps.node_man.models import (
    Host,
    GsePluginDesc,
    ProcessStatus,
)
from common.log import logger


def get_plugin():
    plugins = GsePluginDesc.objects.filter(category="official")
    logger.info(f"get_plugin: Number of plugins [{plugins.count()}]")
    for plugin in plugins:
        yield plugin.name


def update_or_create_process_status(task_id, start, end):
    logger.info(f"{task_id} | get_plugin_status_task: Start updating proc status. [{start}-{end}]")
    hosts = Host.objects.values("bk_host_id", "bk_cloud_id", "inner_ip")[start:end]
    if not hosts:
        # 结束递归
        return
    bk_host_id_map = {}
    query_host = []
    for host in hosts:
        bk_host_id_map[f"{host['bk_cloud_id']}:{host['inner_ip']}"] = host["bk_host_id"]
        query_host.append({"ip": host["inner_ip"], "bk_cloud_id": host["bk_cloud_id"]})

    for proc_name in get_plugin():
        kwargs = {
            "namespace": "nodeman",
            "meta": {"namespace": "nodeman", "name": proc_name, "labels": {"proc_name": proc_name}},
            "hosts": query_host,
        }

        process_status_objs = ProcessStatus.objects.filter(
            name=proc_name, bk_host_id__in=bk_host_id_map.values(), source_type=ProcessStatus.SourceType.DEFAULT
        ).values("bk_host_id", "id")

        process_status_id_map = {}
        for item in process_status_objs:
            process_status_id_map[item["bk_host_id"]] = item["id"]

        need_update_hosts = []
        need_create_hosts = []

        result = client_v2.gse.get_proc_status(kwargs)
        data = result.get("proc_infos", [])

        for proc in data:
            host_key = f"{proc['host']['bk_cloud_id']}:{proc['host']['ip']}"
            version = const.VERSION_PATTERN.search(proc.get("version", ""))
            if bk_host_id_map[host_key] in process_status_id_map.keys():
                need_update_hosts.append(
                    ProcessStatus(
                        id=process_status_id_map[bk_host_id_map[host_key]],
                        status=const.PLUGIN_STATUS_DICT[proc.get("status", 0)],
                        is_auto=const.AUTO_STATUS_DICT[proc.get("isauto", 0)],
                        version=version.group() if version else "",
                    )
                )
            else:
                need_create_hosts.append(
                    ProcessStatus(
                        bk_host_id=bk_host_id_map[host_key],
                        status=const.PLUGIN_STATUS_DICT[proc.get("status", 0)],
                        is_auto=const.AUTO_STATUS_DICT[proc.get("isauto", 0)],
                        version=version.group() if version else "",
                        name=proc.get("meta", {}).get("name").strip(),
                        proc_type=const.ProcType.PLUGIN,
                    )
                )

        ProcessStatus.objects.bulk_update(need_update_hosts, fields=["status", "is_auto", "version"])
        ProcessStatus.objects.bulk_create(need_create_hosts)

    update_or_create_process_status(task_id, end, end + const.QUERY_PLUGIN_STATUS_HOST_LENS)


@periodic_task(
    queue="default",
    options={"queue": "default"},
    run_every=crontab(hour="*", minute="*/15", day_of_week="*", day_of_month="*", month_of_year="*"),
)
def sync_plugin_status_task():
    task_id = sync_plugin_status_task.request.id
    logger.info(f"{task_id} | Start syncing host process status.")
    update_or_create_process_status(task_id, 0, const.QUERY_PLUGIN_STATUS_HOST_LENS)
    logger.info(f"{task_id} | Sync host process status complete.")
