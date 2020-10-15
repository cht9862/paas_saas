# -*- coding: utf-8 -*-
import os

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2019 Tencent BlueKing. All Rights Reserved."

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# 在蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 中获取 APP_ID 和 APP_TOKEN 的值
BK_URL = "https://paas-ee.ied.com"
APP_CODE = os.environ.get("APP_ID", "bk_nodeman")
SECRET_KEY = os.environ.get("APP_TOKEN", "28b7b410-c7b7-4537-9a65-8ce55738170e")
