# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from ..base import ProxyDataAPI, BaseApi


class _CCApi(BaseApi):

    MODULE = _('配置平台')

    def __init__(self):

        self.get_app_list = ProxyDataAPI("查询业务列表")
        # CC3.0 接口
        self.search_host = ProxyDataAPI("批量查询主机详情")
        self.search_inst_by_object = ProxyDataAPI("查询CC对象列表")
        self.search_biz_inst_topo = ProxyDataAPI("查询业务TOPO，显示各个层级")
        self.search_service_instance = ProxyDataAPI("获取服务实例")
        self.search_module = ProxyDataAPI("查询模块")
        self.search_service_category = ProxyDataAPI("查询服务分类")
        self.get_biz_internal_module = ProxyDataAPI("查询内部主机模块")


CCApi = _CCApi()
