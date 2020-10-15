# coding: utf-8
from django.core.management.base import BaseCommand

from apps.node_man.periodic_tasks.resource_watch_task import apply_resource_watched_events


class Command(BaseCommand):
    def handle(self, **kwargs):
        apply_resource_watched_events()
