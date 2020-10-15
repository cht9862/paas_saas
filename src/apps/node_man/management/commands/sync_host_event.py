# coding: utf-8
from django.core.management.base import BaseCommand

from apps.node_man.periodic_tasks.resource_watch_task import sync_resource_watch_host_event


class Command(BaseCommand):
    def handle(self, **kwargs):
        sync_resource_watch_host_event()
