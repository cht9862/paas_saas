# -*- coding: utf-8 -*-
from django.contrib import admin

from common.api.models import DataAPIRecord


class DataAPIRecordAdmin(admin.ModelAdmin):
    list_display = ['request_datetime', 'url', 'module', 'method', 'method_override',
                    'response_result', 'response_code', 'cost_time', 'request_id']
    search_fields = ['url', 'module', 'method', 'request_id', 'query_params', 'response_result']


admin.site.register(DataAPIRecord, DataAPIRecordAdmin)
