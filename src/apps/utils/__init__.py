# -*- coding: utf-8 -*-
import abc

from django.conf import settings


class APIModel(abc.ABC):
    KEYS = []

    @classmethod
    def init_by_data(cls, data):
        kvs = {_key: data[_key] for _key in cls.KEYS}
        o = cls(**kvs)
        o._data = data
        return o

    def __init__(self, *args, **kwargs):
        self._data = None

    def _get_data(self):
        """
        获取基本数据方法，用于给子类重载
        """
        raise NotImplementedError

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()

        return self._data


def build_auth_args(request):
    """
    组装认证信息
    """
    # auth_args 用于ESB身份校验
    auth_args = {}
    if request is None:
        return auth_args

    for k, v in list(settings.OAUTH_COOKIES_PARAMS.items()):
        if v in request.COOKIES:
            auth_args.update({k: request.COOKIES[v]})

    return auth_args
