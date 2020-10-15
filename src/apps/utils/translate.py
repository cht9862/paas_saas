# -*- coding:utf-8 -*-
"""
1. pip install googletrans  安装pip包
2. 在 TO_TRANSLATE_DICT 中放入待翻译的词条
3. python translate.py  执行翻译脚本

需要注意的是，如果一次性请求次数过多（亲测400个以下没问题）
ip地址可能会被谷歌加入黑名单，导致无法再请求调用
"""
from __future__ import unicode_literals

import time

from googletrans import Translator

TO_TRANSLATE_DICT = {
    "中文": "被翻译的语句",
    "提示": "提示语句",
}


def main():
    translator = Translator(service_urls=["translate.google.cn"])
    translated_dict = {}
    for key, value in TO_TRANSLATE_DICT.items():
        translated_dict[key] = translator.translate(value, dest="en").text
        print(f"'{key}': '{translated_dict[key]}',")
        # 睡1秒，避免限频
        time.sleep(1)
    print(translated_dict)


if __name__ == "__main__":
    main()
