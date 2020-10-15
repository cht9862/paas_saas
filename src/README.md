### 本地运行步骤
0. 装好数据库，Python3，若同时开发多个项目，请创建Python虚拟环境
1. 创建数据库 `create database bk_nodeman;`
2. 在config目录下新建`local_settings.py`文件，文件内容为数据库配置，如
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bk_nodeman',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}
```
3. 在根目录下执行脚本拷贝版本文件 linux: `. ./sites/env.sh open`; windows: `sites\env.bat open`
4. 启动工程 `python manage.py runserver 8000`
5. `python manage.py celery worker`
6. `python manage.py celery worker -Q backend`


### 脚本运行参数说明

| 参数 | setup_agent.sh & setup_agent.bat| setup_proxy.sh |
| ---- |----| ---- |
| -I(大写的i)	| 内网网卡IP	| 内网网卡IP |
| -l(小写的L) | 内网下载URL | 外网下载URL |
|-i	|云区域ID	|云区域ID|
|-s|	task_id	|task_id|
|-c|	token |	token|
|-u	|升级（不带参数）|	升级（不带参数）|
|-r|	回调地址(内网URL)	|回调地址（外网URL）|
|-x|	http 代理地址	|http 代理地址|
|-p|	安装路径	|安装路径|
|-n|	上级节点内网IP|	上级节点外网IP|
|-N	|上级节点类型：（server 或 proxy）|	可选，上级节点只能是server|
|-T|	临时文件目录，默认/tmp 或 C:\Windows\Temp\ |	临时文件目录，默认/tmp|
|-R|	卸载|	卸载|
|-v|	设置环境变量	|设置环境变量|
|-o|	配置-v使用，是否覆盖其他选项的环境变量	|配置-v使用，是否覆盖其他选项的环境变量|

| 参数 | setup_pagent.py|
| ---- | ---- |
-l (小写的L) |	外网下载URL
-o | PAgent机器下载安装包的URL
-I (大写的i) |	执行setup_pagent.py脚本的proxy机器的内网网卡IP
-s | task_id
-c | token
-u | 升级
-r | 回调地址（外网URL）
-p | 安装路径
-n | 上级节点ip
-P | 并发数
-f | 配置文件
-j | json格式的配置文件，若与-f同时提供，-f优先
-q | 静默安装，后台执行
-R | 移除
-T | 临时文件目录，默认/tmp