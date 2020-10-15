# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand

from apps.node_man import constants
from apps.node_man.models import Host
from common.api import NodeApi


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        清理老的instance record
        """
        proxy_host_ids = Host.objects.filter(node_type=constants.NodeType.PROXY).values_list("bk_host_id", flat=True)

        params = {
            "run_immediately": True,
            "bk_app_code": "nodeman",
            "bk_username": "admin",
            "scope": {
                "node_type": "INSTANCE",
                "object_type": "HOST",
                "nodes": [{"bk_host_id": bk_host_id} for bk_host_id in proxy_host_ids],
            },
            "steps": [
                {"id": "agent", "type": "AGENT", "config": {"job_type": "UPGRADE_PROXY"}, "params": {"context": {}}}
            ],
        }
        NodeApi.create_subscription(params)
