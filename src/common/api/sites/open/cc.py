# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from common.api.base import DataAPI
from common.api.modules.utils import add_esb_info_before_request
from config.domains import CC_APIGATEWAY_ROOT_V2


class _CCApi(object):
    MODULE = _('配置平台')

    def __init__(self):
        self.get_app_list = DataAPI(
            method='POST',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_business/',
            module=self.MODULE,
            description='查询业务列表',
            before_request=add_esb_info_before_request,
            cache_time=60
        )
        self.search_inst_by_object = DataAPI(
            method='POST',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_inst_by_object/',
            module=self.MODULE,
            description='查询CC对象列表',
            before_request=add_esb_info_before_request
        )
        self.search_biz_inst_topo = DataAPI(
            method='POST',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_biz_inst_topo/',
            module=self.MODULE,
            description='查询业务TOPO，显示各个层级',
            before_request=add_esb_info_before_request
        )
        self.search_host = DataAPI(
            method='POST',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_host/',
            module=self.MODULE,
            description='批量查询主机详情',
            before_request=add_esb_info_before_request
        )
        # todo url 看看3.0怎么弄的
        self.search_service_instance = DataAPI(
            method='POST',
            url='https://cmdbee-dev.bktencent.com/api/v3/findmany/proc/service_instance',
            module=self.MODULE,
            description='获取服务实例',
            before_request=add_esb_info_before_request
        )
        self.search_module = DataAPI(
            method='POST',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_module',
            module=self.MODULE,
            description='查询模块',
            before_request=add_esb_info_before_request,
        )
        self.get_host_info = DataAPI(
            method='GET',
            url=CC_APIGATEWAY_ROOT_V2 + 'search_module',
            module=self.MODULE,
            description='查询模块',
            before_request=add_esb_info_before_request,
        )
        self.search_service_category = DataAPI(
            method='POST',
            url='https://cmdbee-dev.bktencent.com/api/v3/findmany/proc/service_category',
            module=self.MODULE,
            description='查询服务分类',
            before_request=add_esb_info_before_request,
        )
        self.get_biz_internal_module = DataAPI(
            method='GET',
            url=CC_APIGATEWAY_ROOT_V2 + 'get_biz_internal_module',
            module=self.MODULE,
            description='查询内部业务模块',
            before_request=add_esb_info_before_request,
        )


CCApi = _CCApi()
