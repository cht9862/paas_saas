# coding: utf-8


from django.core.management.base import BaseCommand

from apps.node_man.periodic_tasks import sync_cmdb_host


class Command(BaseCommand):
    def handle(self, **kwargs):
        sync_cmdb_host()
