# -*- coding: utf-8 -*-
from multiprocessing.pool import ThreadPool


def batch_request(func, params, get_data=lambda x: x["info"], get_count=lambda x: x["count"], limit=500):
    """
    异步并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :return: 请求结果
    """

    # 如果该接口没有返回count参数，只能同步请求
    if not get_count:
        return sync_batch_request(func, params, get_data, limit)

    # 请求第一次获取总数
    result = func(page={"start": 0, "limit": 1}, **params)
    count = get_count(result)
    data = []
    start = 0

    # 根据请求总数并发请求
    pool = ThreadPool(20)
    futures = []
    while start < count:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        futures.append(pool.apply_async(func, kwds=request_params))

        start += limit

    pool.close()
    pool.join()

    # 取值
    for future in futures:
        data.extend(get_data(future.get()))

    return data


def sync_batch_request(func, params, get_data=lambda x: x["info"], limit=500):
    """
    同步请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param limit: 一次请求数量
    :return: 请求结果
    """
    # 如果该接口没有返回count参数，只能同步请求
    data = []
    start = 0

    # 根据请求总数并发请求
    while True:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        result = get_data(func(request_params))
        data.extend(result)
        if len(result) < limit:
            break
        else:
            start += limit

    return data
