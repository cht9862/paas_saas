# -*- coding: utf-8 -*-


from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "apps.backend"
    verbose_name = "Backend"

    def ready(self):
        from apps.backend.plugin.signals import activity_failed_handler
        from pipeline.engine.signals import activity_failed

        activity_failed.connect(activity_failed_handler, dispatch_uid="_activity_failed")
