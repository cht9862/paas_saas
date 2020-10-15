# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings

from apps.node_man.constants import BkappRunEnvType


def init_gse_port_config(apps, schema_editor):
    # 设置接入点端口信息
    AccessPoint = apps.get_model("node_man", "AccessPoint")
    AccessPoint.objects.update(
        port_config={
            "io_port": 48533 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 48668,
            "trunk_port": 48331 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 48329,
            "db_proxy_port": 58817 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 58859,
            "file_svr_port": 59173 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 58925,
            "data_port": 58625 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 58625,
            "bt_port_start": 60020 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 60020,
            "bt_port_end": 60030 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 60030,
            "agent_thrift_port": 48669 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 48669,
            "btsvr_thrift_port": 58930 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 58930,
            "api_server_port": 50002 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 50002,
            "proc_port": 50000 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 50000,
            "bt_port": 10020 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 10020,
            "tracker_port": 10030 if settings.BKAPP_RUN_ENV == BkappRunEnvType.ce else 10030,
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ("node_man", "0015_accesspoint_port_config"),
    ]

    operations = [
        migrations.RunPython(init_gse_port_config),
    ]
