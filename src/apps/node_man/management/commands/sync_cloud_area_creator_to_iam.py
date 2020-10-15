# coding: utf-8


from django.core.management.base import BaseCommand

from apps.node_man.iam_provider import sync_cloud_area_creator_to_iam


class Command(BaseCommand):
    def handle(self, **kwargs):
        sync_cloud_area_creator_to_iam()
