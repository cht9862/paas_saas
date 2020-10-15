# -*- coding: utf-8 -*-
from celery.task import task

from pipeline.service import task_service


@task(ignore_result=True)
def callback(*args, **kwargs):
    task_service.callback(*args, **kwargs)
