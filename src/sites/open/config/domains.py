# -*- coding: utf-8 -*-
import os
from django.conf import settings

BK_PAAS_HOST = settings.BK_PAAS_INNER_HOST or settings.BK_PAAS_HOST or ""
ESB_PREFIX = "/api/c/compapi/"
ESB_PREFIX_V2 = "/api/c/compapi/v2/"
SELF_API_PREFIX = "/api/c/self-service-api/"

# 蓝鲸平台模块域名
BK_LOGIN_APIGATEWAY_ROOT = BK_PAAS_HOST + ESB_PREFIX + "bk_login/"
BK_PAAS_APIGATEWAY_ROOT = BK_PAAS_HOST + ESB_PREFIX + "bk_paas/"

CC_APIGATEWAY_ROOT_V2 = BK_PAAS_HOST + ESB_PREFIX_V2 + "cc/"
GSE_APIGATEWAY_ROOT_V2 = BK_PAAS_HOST + ESB_PREFIX_V2 + "gse/"
ESB_APIGATEWAY_ROOT_V2 = BK_PAAS_HOST + ESB_PREFIX_V2 + "esb/"

# 节点管理
BK_NODE_APIGATEWAY_ROOT = os.getenv("BKAPP_BK_NODE_APIGATEWAY", BK_PAAS_HOST + ESB_PREFIX_V2 + "nodeman/")
