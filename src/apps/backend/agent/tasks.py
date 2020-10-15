# -*- coding: utf-8 -*-
import traceback

from apps.backend.celery import app
from apps.backend.utils.ssh import SshMan
from apps.backend.utils.wmi import execute_cmd
from apps.node_man import constants
from apps.node_man.models import Host
from apps.utils.basic import suffix_slash

from common.log import logger

from pipeline.log.models import LogEntry


def collect_log_exception_handler(collect_log_func):
    """日志收集处理装饰器：捕获SshMan抛出异常并记录到LogEntry
    :param collect_log_func: collect_log方法
    :return:
    """

    def exception_handler(bk_host_id, node_id=None):
        try:
            collect_log_func(bk_host_id, node_id)
        except Exception as e:
            insert_logs(
                "Collect log failed[{error}]: {exception_detail}".format(
                    error=e, exception_detail=traceback.format_exc()
                ),
                node_id,
            )

    return exception_handler


@app.task(queue="backend")
@collect_log_exception_handler
def collect_log(bk_host_id, node_id=None):
    host = Host.get_by_host_info({"bk_host_id": bk_host_id})
    dest_dir = host.agent_config["temp_path"]
    dest_dir = suffix_slash(host.os_type.lower(), dest_dir)
    ssh_man = None
    if host.node_type == constants.NodeType.PAGENT:
        # @TODO PAGENT的日志采集需要通过作业平台
        return None
        # PAEGNT 需要登录 PROXY，在 PROXY 上报日志
    #         proxy = host.get_random_alive_proxy()
    #         proxy_dest_dir = proxy.ap.agent_config["linux"]["temp_path"]
    #         proxy_dest_dir = suffix_slash("linux", proxy_dest_dir)
    #         ssh_man = SshMan(proxy, logger)
    #         if host.os_type.lower() == "linux":
    #             cmd = f"""\
    # /opt/py36/bin/python -c '\
    # import sys;\
    # sys.path.append("{proxy_dest_dir}");\
    # from setup_pagent import SshMan;\
    # ssh = SshMan("{host.login_ip or host.inner_ip}", {host.identity.port},
    #  "{host.identity.account}", "{host.identity.password}");\
    # ssh.get_and_set_prompt();\
    # res = ssh.send_cmd("cat {dest_dir}nm.setup_agent.sh.{node_id}.debug", check_output=False);\
    # print(res)'
    # """
    #             output = ssh_man.send_cmd(cmd, is_clear_cmd_and_prompt=False, check_output=False)
    #             output = output.replace(f'SshMan(""{host.identity.password}");', 'SshMan(""********");',)
    #         else:
    #             dest_dir = "".join([char if char != "\\" else "\\\\" for char in dest_dir])
    #             write_code_cmd = f"""echo '\
    # import sys;\
    # sys.path.append("{proxy_dest_dir}");\
    # from setup_pagent import execute_cmd;\
    # execute_cmd("type {dest_dir}nm.setup_agent.bat.{node_id}.debug",
    # "{host.login_ip or host.inner_ip}","{host.identity.account}", "{host.identity.password}", "", noOutput=False);' \
    # > {proxy_dest_dir}collect_win_log_{node_id}.py
    # """
    #             ssh_man.send_cmd(write_code_cmd)
    #             cmd = f"/opt/py36/bin/python {proxy_dest_dir}collect_win_log_{node_id}.py"
    #             output = ssh_man.send_cmd(cmd, is_adding_output=True, check_output=False)
    #             ssh_man.send_cmd("rm -f {proxy_dest_dir}collect_win_log_{node_id}.py")
    elif host.node_type == constants.NodeType.PROXY:
        ssh_man = SshMan(host, logger)
        # 一定要先设置一个干净的提示符号，否则会导致console_ready识别失效
        ssh_man.get_and_set_prompt()
        output = ssh_man.send_cmd(
            f"cat {dest_dir}nm.setup_proxy.sh.{node_id}.debug", is_clear_cmd_and_prompt=False, check_output=False,
        )
    else:
        if host.os_type.lower() == "linux":
            ssh_man = SshMan(host, logger)
            # 一定要先设置一个干净的提示符号，否则会导致console_ready识别失效
            ssh_man.get_and_set_prompt()
            output = ssh_man.send_cmd(
                f"cat {dest_dir}nm.setup_agent.sh.{node_id}.debug", is_clear_cmd_and_prompt=False, check_output=False,
            )
        else:
            output = execute_cmd(
                f"type {dest_dir}nm.setup_agent.bat.{node_id}.debug",
                host.login_ip or host.inner_ip,
                host.identity.account,
                host.identity.password,
            )["data"]
    if ssh_man:
        ssh_man.safe_close(ssh_man.ssh)
    insert_logs(output, node_id)


def insert_logs(logs, node_id):
    # 覆盖原子日志
    insert_log(" Begin of collected logs: ".center(100, "*"), node_id)
    message = f"[collect] {logs}"
    insert_log(message, node_id)
    insert_log(" End of collected logs ".center(100, "*"), node_id)


def insert_log(message, node_id, level="DEBUG"):
    LogEntry.objects.create(
        logger_name="pipeline.logging", level_name=level, message=message, node_id=node_id,
    )
