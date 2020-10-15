# -*- coding: utf-8 -*-

# 动作轮询间隔
from __future__ import absolute_import, unicode_literals

from celery.schedules import crontab

ACTION_POLLING_INTERVAL = 1
# 动作轮询超时时间
ACTION_POLLING_TIMEOUT = 60 * 3 * ACTION_POLLING_INTERVAL

# 自动下发触发周期
SUBSCRIPTION_UPDATE_INTERVAL = crontab(hour="*", minute="*/15", day_of_week="*", day_of_month="*", month_of_year="*")

# 订阅任务清理周期
INSTANCE_CLEAR_INTERVAL = crontab(minute="*/5", hour="*", day_of_week="*", day_of_month="*", month_of_year="*")

# 任务超时时间。距离 create_time 多久后会被判定为超时，防止 pipeline 后台僵死的情况
TASK_TIMEOUT = 60 * 15

# 最大重试次数
MAX_RETRY_TIME = 10

# 自动下发 - 订阅配置单个切片所包含的最大订阅个数 (根据经验，一个订阅需要消耗1~2s）
SUBSCRIPTION_UPDATE_SLICE_SIZE = 50
