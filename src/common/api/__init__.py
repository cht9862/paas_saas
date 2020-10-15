# -*- coding: utf-8 -*-

"""
API 统一调用模块，使用方式，举例
>>> from common.api import DataQueryApi
>>> DataQueryApi.query({})
"""
from django.apps import AppConfig
from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string


def new_api_module(module_name, api_name, module_dir='modules'):
    mod = 'common.api.{modules}.{mod}.{api}'.format(modules=module_dir, mod=module_name, api=api_name)
    return import_string(mod)()


# 对请求模块设置懒加载机制，避免项目启动出现循环引用，或者 model 提前加载

# 蓝鲸平台模块域名
BKLoginApi = SimpleLazyObject(lambda: new_api_module('bk_login', '_BKLoginApi'))
BKPAASApi = SimpleLazyObject(lambda: new_api_module('bk_paas', '_BKPAASApi'))
CCApi = SimpleLazyObject(lambda: new_api_module('cc', '_CCApi'))
BKAuthApi = SimpleLazyObject(lambda: new_api_module('bk_auth', '_BKAuthApi'))
# CMSI
CmsiApi = SimpleLazyObject(lambda: new_api_module('cmsi', '_CmsiApi'))

# 节点管理
NodeApi = SimpleLazyObject(lambda: new_api_module('bk_node', '_BKNodeApi'))

# ESB
EsbApi = SimpleLazyObject(lambda: new_api_module('esb', '_ESBApi'))

__all__ = [
    'BKLoginApi', 'BKPAASApi', 'CCApi', 'CmsiApi', "NodeApi", 'BKAuthApi',
]


class ApiConfig(AppConfig):
    name = 'common.api'
    verbose_name = 'ESB_API'

    def ready(self):
        pass


default_app_config = 'common.api.ApiConfig'
