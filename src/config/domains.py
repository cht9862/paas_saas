# -*- coding: utf-8 -*-
from django.conf import settings


API_ROOTS = [
    # 蓝鲸平台模块域名
    'BK_LOGIN_APIGATEWAY_ROOT',
    'BK_PAAS_APIGATEWAY_ROOT',
    'CC_APIGATEWAY_ROOT_V2',

    'GSE_APIGATEWAY_ROOT_V2',
    'ESB_APIGATEWAY_ROOT_V2',

    # 节点管理
    'BK_NODE_APIGATEWAY_ROOT',

]

domain_module = 'sites.{}.config.domains'.format(settings.RUN_VER)
module = __import__(domain_module, globals(), locals(), ['*'])

for _root in API_ROOTS:
    try:
        locals()[_root] = getattr(module, _root)
    except Exception:
        pass

__all__ = API_ROOTS
