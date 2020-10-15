# coding: utf-8


from django.core.management.base import BaseCommand

from apps.utils.generate_api_js import main


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-g", "--is_apigw", action="store_true", help="whether for api_gateway")

    def handle(self, **kwargs):
        main(kwargs["is_apigw"])
