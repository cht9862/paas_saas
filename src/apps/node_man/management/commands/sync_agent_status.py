# coding: utf-8


from django.core.management.base import BaseCommand

from apps.node_man.periodic_tasks import sync_agent_status_task


class Command(BaseCommand):
    def handle(self, **kwargs):
        sync_agent_status_task()
