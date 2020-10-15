# -*- coding: utf-8 -*-
import os

from django.apps.config import AppConfig
from django.conf import settings

from common.log import logger

try:
    from blueapps.utils.esbclient import get_client_by_user
except Exception:
    pass


class ApiConfig(AppConfig):
    name = "apps.node_man"
    verbose_name = "NODE_MAN"

    def ready(self):
        self.fetch_esb_api_key()
        self.judge_use_tjj()
        return True

    @staticmethod
    def fetch_esb_api_key():
        """
        企业版获取JWT公钥并存储到全局配置中
        """
        if hasattr(settings, "APIGW_PUBLIC_KEY") or os.environ.get("BKAPP_APIGW_CLOSE"):
            return
        from apps.node_man.models import GlobalSettings

        try:
            # 使用 first 防止存在两条相同的 config_id
            config = GlobalSettings.objects.filter(key="APIGW_PUBLIC_KEY").first()
        except Exception:
            config = None

        if config:
            # 从数据库取公钥，若存在，直接使用
            settings.APIGW_PUBLIC_KEY = config.v_json
            message = "[ESB][JWT]get esb api public key success (from db cache)"
            # flush=True 实时刷新输出
            logger.info(message)
        else:
            if settings.RUN_MODE == "DEVELOP":
                return

            client = get_client_by_user(user_or_username=settings.SYSTEM_USE_API_ACCOUNT)
            esb_result = client.esb.get_api_public_key()
            if esb_result["result"]:
                api_public_key = esb_result["data"]["public_key"]
                settings.APIGW_PUBLIC_KEY = api_public_key
                # 获取到公钥之后回写数据库
                try:
                    GlobalSettings.objects.update_or_create(
                        key="APIGW_PUBLIC_KEY", defaults={"v_json": api_public_key},
                    )
                except Exception:
                    pass
                message = "[ESB][JWT]get esb api public key success (from realtime api)"
                logger.info(message)
            else:
                message = f'[ESB][JWT]get esb api public key error:{esb_result["message"]}'
                logger.warning(message)
                raise Exception(message)

    @staticmethod
    def judge_use_tjj():
        """
        判断是否使用铁将军，目前上云版和运维环境使用
        读取DB后写入settings内存中，避免多次查表
        """
        from apps.node_man.models import GlobalSettings

        try:
            obj, created = GlobalSettings.objects.get_or_create(key="USE_TJJ", defaults=dict(v_json=False))
            settings.USE_TJJ = obj.v_json
        except Exception:
            message = "USE_TJJ Variable acquisition failed."
            logger.info(message)
