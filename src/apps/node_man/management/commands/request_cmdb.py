# coding: utf-8


from django.core.management.base import BaseCommand

from apps.component.esbclient import client_v2
from apps.utils.batch_request import batch_request


class Command(BaseCommand):
    def handle(self, **kwargs):
        params = {}
        batch_request(client_v2.cc.list_hosts_without_biz, params)
