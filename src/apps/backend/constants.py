# -*- coding: utf-8 -*-

from __future__ import unicode_literals

########################################################################################################
# PARAMIKO 相关配置
########################################################################################################
RECV_BUFLEN = 32768  # SSH通道recv接收缓冲区大小
RECV_TIMEOUT = 60  # SSH通道recv超时 RECV_TIMEOUT秒
SSH_CON_TIMEOUT = 10  # SSH连接超时设置10s
MAX_WAIT_OUTPUT = 32  # 最大重试等待recv_ready次数
SLEEP_INTERVAL = 1  # recv等待间隔


class TargetNodeType(object):
    """
    目标节点类型
    """

    TOPO = "TOPO"  # 动态实例（拓扑）
    INSTANCE = "INSTANCE"  # 静态实例
    SERVICE_TEMPLATE = "SERVICE_TEMPLATE"  # 服务模板
    SET_TEMPLATE = "SET_TEMPLATE"  # 集群模板
