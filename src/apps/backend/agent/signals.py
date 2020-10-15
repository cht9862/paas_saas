# -*- coding: utf-8 -*-
from django.dispatch import receiver

from apps.backend.subscription.tools import update_job_status
from pipeline.engine.signals import activity_failed, pipeline_end, pipeline_revoke


@receiver(pipeline_end)
def pipeline_end_handler(sender, root_pipeline_id, **kwargs):
    pass


@receiver(activity_failed)
def activity_failed_handler(pipeline_id, *args, **kwargs):
    update_job_status(pipeline_id, False)


@receiver(pipeline_revoke)
def pipeline_revoke_handler(sender, root_pipeline_id, **kwargs):
    update_job_status(root_pipeline_id)
