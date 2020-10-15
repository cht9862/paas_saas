# coding: utf-8


from django.core.management.base import BaseCommand

from apps.component.esbclient import client_v2
from apps.node_man.models import Cloud


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-c", "--bk_cloud_id", type=int, help="cloud id")
        parser.add_argument("-b", "--bk_biz_id", type=int, help="biz id")

    def handle(self, *args, **kwargs):
        bk_biz_maintainer = (
            client_v2.cc.search_business(
                {
                    "fields": ["bk_biz_id", "bk_biz_name", "bk_biz_maintainer"],
                    "condition": {"bk_biz_id": kwargs["bk_biz_id"]},
                }
            )["info"][0]
            .get("bk_biz_maintainer", "")
            .split(",")
        )
        cloud = Cloud.objects.get(bk_cloud_id=kwargs["bk_cloud_id"])
        cloud.creator = bk_biz_maintainer
        cloud.save()
