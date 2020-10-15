# -*- coding: utf-8 -*-
import random
import time

from django.core.cache import cache
from django.db.utils import IntegrityError

from apps.component.esbclient import client_v2
from apps.node_man.periodic_tasks.sync_cmdb_host import (
    update_or_create_host_base,
    _generate_host,
)
from apps.node_man import constants as const
from apps.node_man.models import IdentityData, Host, ProcessStatus, ResourceWatchEvent, AccessPoint, GlobalSettings


RESOURCE_WATCH_HOST_CURSOR_KEY = "resource_watch_host_cursor"
RESOURCE_WATCH_HOST_RELATION_CURSOR_KEY = "resource_watch_host_relation_cursor"
APPLY_RESOURCE_WATCHED_EVENTS_KEY = "apply_resource_watched_events"


def set_cursor(data, cursor_key):
    new_cursor = data["bk_events"][-1]["bk_cursor"]
    cache.set(cursor_key, new_cursor, 120)


def random_key():
    return "{}{}{}".format(
        int(time.time()), random.randint(10000, 99999), "".join(random.sample(str(int(time.time())), 5))
    )


def is_lock(config_key, id_key):
    """
    此函数用于多机部署时标识当前是否是自己在跑
    :param config_key: 数据库记录相关信息的键
    :param id_key: 标识自己的key
    """
    current_time = int(time.time())
    config = GlobalSettings.get_config(key=config_key, default={})
    if not config.get("key"):
        # 没有key开始抢占
        try:
            GlobalSettings.set_config(key=config_key, value={"key": id_key, "time": current_time})
        except IntegrityError:
            # 说明已被其它进程设置本进程不处理
            return False
    elif current_time - config["time"] > 60:
        # 说明key过期开始抢占
        # 先删除等待70s后创建以消除多机部署的时间差
        try:
            GlobalSettings.objects.get(key=config_key).delete()
        except GlobalSettings.DoesNotExist:
            pass

        # 防止同一进程瞬间创建
        time.sleep(70)

        try:
            GlobalSettings.set_config(key=config_key, value={"key": id_key, "time": current_time})
        except IntegrityError:
            return False
    elif config["key"] != id_key:
        # 说明不是自己
        return False

    else:
        # 说明为自己更新key
        GlobalSettings.update_config(key=config_key, value={"key": id_key, "time": current_time})

    return True


def _resource_watch(cursor_key, kwargs):
    # 用于标识自己
    id_key = random_key()
    while True:
        if not is_lock(cursor_key, id_key):
            time.sleep(60)
            continue

        bk_cursor = cache.get(cursor_key)
        if bk_cursor:
            kwargs["bk_cursor"] = bk_cursor

        data = client_v2.cc.resource_watch(kwargs)
        if not data["bk_watched"]:
            # 记录最新cursor
            set_cursor(data, cursor_key)
            continue

        objs = []
        for event in data["bk_events"]:
            if cursor_key == RESOURCE_WATCH_HOST_RELATION_CURSOR_KEY and event["bk_event_type"] == "delete":
                # 不记录主机关系的删除事件
                continue
            objs.append(
                ResourceWatchEvent(
                    bk_cursor=event["bk_cursor"],
                    bk_event_type=event["bk_event_type"],
                    bk_resource=event["bk_resource"],
                    bk_detail=event["bk_detail"],
                )
            )

        ResourceWatchEvent.objects.bulk_create(objs)

        # 记录最新cursor
        set_cursor(data, cursor_key)


def sync_resource_watch_host_event():
    """
    拉取主机事件
    """
    kwargs = {
        "bk_resource": const.ResourceType.host,
        "bk_fields": ["bk_host_innerip", "bk_os_type", "bk_host_id", "bk_cloud_id", "bk_host_outerip"],
    }

    _resource_watch(RESOURCE_WATCH_HOST_CURSOR_KEY, kwargs)


def sync_resource_watch_host_relation_event():
    """
    拉取主机关系事件
    """
    kwargs = {
        "bk_resource": const.ResourceType.host_relation,
    }

    _resource_watch(RESOURCE_WATCH_HOST_RELATION_CURSOR_KEY, kwargs)


def delete_host(bk_host_id):
    Host.objects.filter(bk_host_id=bk_host_id).delete()
    IdentityData.objects.filter(bk_host_id=bk_host_id).delete()
    ProcessStatus.objects.filter(bk_host_id=bk_host_id).delete()


def list_biz_host(bk_biz_id, bk_host_id):
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_host_outerip", "bk_os_type", "bk_os_name"],
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": "bk_host_id", "operator": "equal", "value": bk_host_id}],
        },
        "page": {"start": 0, "limit": 1},
    }
    data = client_v2.cc.list_biz_hosts(kwargs)
    if data.get("info") or []:
        return data["info"][0]
    return {}


def apply_resource_watched_events():
    id_key = random_key()
    config_key = APPLY_RESOURCE_WATCHED_EVENTS_KEY

    while True:
        if not is_lock(config_key, id_key):
            time.sleep(60)
            continue

        event = ResourceWatchEvent.objects.order_by("create_time").first()
        if not event:
            time.sleep(10)
            continue

        if event.bk_event_type in ["update", "create"] and event.bk_resource == const.ResourceType.host:
            _, need_delete_host_ids = update_or_create_host_base(None, None, [event.bk_detail])
            if need_delete_host_ids:
                delete_host(need_delete_host_ids[0])
        elif event.bk_event_type in ["create"] and event.bk_resource == const.ResourceType.host_relation:
            # 查询主机信息创建或者更新
            bk_host_id = event.bk_detail["bk_host_id"]
            host_obj = Host.objects.filter(bk_host_id=bk_host_id).first()
            if host_obj:
                if host_obj.bk_biz_id != event.bk_detail["bk_biz_id"]:
                    # 更新业务
                    host_obj.bk_biz_id = event.bk_detail["bk_biz_id"]
                    host_obj.save()
            else:
                host = list_biz_host(event.bk_detail["bk_biz_id"], bk_host_id)
                if host:
                    ap_id = const.DEFAULT_AP_ID if AccessPoint.objects.count() > 1 else AccessPoint.objects.first().id
                    host_data, identify_data, process_status_data = _generate_host(
                        event.bk_detail["bk_biz_id"], host, host["bk_host_innerip"], host["bk_host_outerip"], ap_id
                    )
                    # 与注册CC原子存在同时写入的可能，防止更新进行强制插入
                    try:
                        host_data.save(force_insert=True)
                        identify_data.save(force_insert=True)
                        process_status_data.save(force_insert=True)
                    except IntegrityError:
                        pass

        elif event.bk_event_type in ["delete"]:
            delete_host(event.bk_detail["bk_host_id"])

        # 删除事件记录
        event.delete()
