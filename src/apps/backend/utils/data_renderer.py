# -*- coding: utf-8 -*-
"""
jinja2渲染相关的公共函数
"""
import copy

import six
from jinja2 import Template


def find_element(element, dict_data):
    """
    根据路径字符串获取字典定义的嵌套key的值
    :param element: 路径字符串，格式 a.b.c.d
    :param dict_data: 字典数据
    :return: value
    """
    keys = element.split(".")
    rv = dict_data
    for key in keys:
        rv = rv[key]
    return rv


def nested_render_data(data, context):
    """
    递归渲染字典中的模板字符串
    """
    if isinstance(data, six.string_types):
        try:
            # 尝试渲染用户参数，一旦失败，立即返回原数据
            template = Template(data)
            return template.render(context)
        except Exception:
            return data
    elif isinstance(data, dict):
        if "$for" in data and "$item" in data and "$body" in data:
            # 循环动态变量解析
            data_list = []
            # 提取列表变量
            for_list = find_element(data["$for"], context)

            for item in for_list:
                # 临时设置上下文
                context[data["$item"]] = item
                # 深拷贝一次，防止原始模板被修改
                body_data = copy.deepcopy(data["$body"])
                data_list.append(nested_render_data(body_data, context))
                # 恢复上下文
                context.pop(data["$item"])
            return data_list

        for key, value in data.items():
            data[key] = nested_render_data(value, context)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            data[index] = nested_render_data(value, context)
    return data
