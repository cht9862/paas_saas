# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from ..base import ProxyDataAPI, BaseApi


class _BKPAASApi(BaseApi):

    MODULE = _('PaaS平台')

    def __init__(self):
        self.get_app_info = ProxyDataAPI("获取app信息")


BKPAASApi = _BKPAASApi()
