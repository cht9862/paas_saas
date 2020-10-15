# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DataAPIRecord(models.Model):

    request_datetime = models.DateTimeField()
    url = models.CharField(max_length=128, db_index=True)
    module = models.CharField(max_length=64, db_index=True)
    method = models.CharField(max_length=16)
    method_override = models.CharField(max_length=16, null=True)
    query_params = models.TextField()

    response_result = models.BooleanField()
    response_code = models.CharField(max_length=16, db_index=True)
    response_data = models.TextField()
    response_message = models.CharField(max_length=1024, null=True)
    response_errors = models.TextField(null=True, default=None)

    cost_time = models.FloatField()
    request_id = models.CharField(max_length=64, db_index=True)

    class Meta:
        verbose_name = _("【平台日志】API调用日志")
        verbose_name_plural = _("【平台日志】API调用日志")
        app_label = 'api'
