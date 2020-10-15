# -*- coding: utf-8 -*-
import time

import ujson as json
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.backend.utils.data_renderer import nested_render_data
from apps.node_man import constants
from apps.node_man.models import Host, aes_cipher
from blueapps.account.decorators import login_exempt
from common.log import logger
from pipeline.service import task_service

AGENT_TEMPLATE = """
{
    "log": {{ log_path }},
    "logfilesize": 10,
    "logfilenum": 10,
    {%- if password_keyfile %}
    "password_keyfile": {{ password_keyfile }},
    {%- endif %}
    "cert": {{ cert }},
    "proccfg": {{ proccfg }},
    "procgroupcfg": {{ procgroupcfg }},
    "alarmcfgpath": {{ alarmcfgpath }},
    "dataipc": {{ dataipc }},
    "runmode": 1,
    "alliothread": 8,
    "workerthread": 24,
    "level": "error",
    "ioport": {{ io_port }},
    "filesvrport": {{ file_svr_port }},
    "dataport": {{ data_port}},
    "btportstart": {{ bt_port_start }},
    "btportend": {{ bt_port_end }},
    "agentip": "{{ agentip }}",
    "identityip": "{{ identityip }}",
    "dftregid": "{{ region_id }}",
    "dftcityid": "{{ city_id }}",
    "bizid": {{ bk_supplier_id }},
    "cloudid": {{ bk_cloud_id }},
    "recvthread": 5,
    "timeout": 120,
    "tasknum": 100,
    "thriftport": {{ agent_thrift_port }},
    "trunkport": {{ trunk_port }},
    "dbproxyport": {{ db_proxy_port }},
    "apiserverport": {{ api_server_port }},
    "procport": {{ proc_port }},
    "peer_exchange_switch_for_agent": {{ peer_exchange_switch_for_agent }},
    {%- if bt_speed_limit %}
    "btSpeedLimit": {{ bt_speed_limit }},
    {%- endif -%}
    {% if bk_cloud_id == default_cloud_id %}
    "zkhost": "{{ zkhost }}",
    "zkauth": "{{ zkauth }}"
    {% else %}
    "btfileserver": [
        {% for server in proxy_servers%}
            {
                "ip": "{{ server }}",
                "port": {{ file_svr_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "dataserver": [
        {% for server in proxy_servers%}
            {
                "ip": "{{ server }}",
                "port": {{ data_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "taskserver": [
        {% for server in proxy_servers%}
            {
                "ip": "{{ server }}",
                "port": {{ io_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "btserver_is_bridge": 0,
    "btserver_is_report": 1
    {% endif %}
}
"""

PROXY_TEMPLATE = """
{
    "log": "{{ log_path }}",
    "logfilesize": 10,
    "logfilenum": 10,
    {%- if password_keyfile %}
    "password_keyfile": "{{ setup_path }}/proxy/cert/cert_encrypt.key",
    {%- endif %}
    "cert": "{{ setup_path }}/proxy/cert",
    "proccfg": "{{ setup_path }}/proxy/etc/procinfo.json",
    "procgroupcfg": "{{ setup_path }}/proxy/etc/procgroupinfo.json",
    "alarmcfgpath": "{{ setup_path }}/plugins/etc",
    "dataipc": "{{ dataipc }}",
    "runmode": 0,
    "alliothread": 8,
    "workerthread": 24,
    "level": "error",
    "ioport": {{ io_port }},
    "filesvrport": {{ file_svr_port }},
    "btportstart": {{ bt_port_start }},
    "btportend": {{ bt_port_end }},
    "proxylistenip": "{{ inner_ip }}",
    "agentip": "{{ inner_ip }}",
    "identityip": "{{ inner_ip }}",
    "peer_exchange_switch_for_agent": {{ peer_exchange_switch_for_agent }},
    {%- if bt_speed_limit %}
    "btSpeedLimit": {{ bt_speed_limit }},
    {%- endif -%}
    "proxytaskserver": [
        {% for gse_outer_ip in taskserver_outer_ips%}
            {
                "ip": "{{ gse_outer_ip }}",
                "port": {{ io_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "btfileserver": [
        {% for proxy_server in proxy_servers%}
            {
                "ip": "{{ proxy_server }}",
                "port": {{ file_svr_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "dataserver": [
        {% for proxy_server in proxy_servers%}
            {
                "ip": "{{ proxy_server }}",
                "port": {{ data_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "taskserver": [
        {% for proxy_server in proxy_servers%}
            {
                "ip": "{{ proxy_server }}",
                "port": {{ io_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "bizid": {{ bk_supplier_id }},
    "cloudid": {{ bk_cloud_id }},
    "dftregid": "{{ region_id }}",
    "dftcityid": "{{ city_id }}",
    "btserver_is_bridge": 0,
    "btserver_is_report": 1
}"""

BTSVR_TEMPLATE = """
{
    "log": "{{ log_path }}",
    "logfilesize": 10,
    "logfilenum": 10,
    "runtimedata": "{{ data_path }}",
    {%- if password_keyfile %}
    "password_keyfile": "{{ setup_path }}/proxy/cert/cert_encrypt.key",
    {%- endif %}
    "cert": "{{ setup_path }}/proxy/cert",
    "alliothread": 8,
    "workerthread": 24,
    "level": "error",
    "filesvrport": {{ file_svr_port }},
    "btportstart": {{ bt_port_start }},
    "btportend": {{ bt_port_end }},
    "dftregid": "{{ region_id }}",
    "dftcityid": "{{ city_id }}",
    "btserver_is_bridge": 0,
    "btserver_is_report": 1,
    "btzkflag": 0,
    "filesvrthriftip": "0.0.0.0",
    "btServerInnerIP": [{"ip": "{{ inner_ip }}", "port": {{ btsvr_thrift_port }}}],
    // 该处填写 PROXY 所在的外网 ip
    "btServerOuterIP": [{"ip": "{{ outer_ip }}", "port": {{ btsvr_thrift_port }}}],

    // 以下填写 gse 所在的外网 ip
    "btfilesvrscfg": [
        {% for gse_outer_ip in btfileserver_outer_ips%}
            {
                "ip": "{{ gse_outer_ip }}",
                "compId": "0",
                "isTransmit": 0,
                "tcpPort": {{ file_svr_port }},
                "thriftPort": {{ btsvr_thrift_port }},
                "btPort": {{ bt_port }},
                "trackerPort": {{ tracker_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "dataid": 1000,
    "bizid": {{ bk_supplier_id }},
    "cloudid": {{ bk_cloud_id }}
}"""

TRANSIT_TEMPLATE = """
{
    "log": "{{ log_path }}",
    "logfilesize": 10,
    "logfilenum": 10,
    "runtimedata": "{{ data_path }}",
    {% if password_keyfile %}
    "password_keyfile": "{{ setup_path }}/proxy/cert/cert_encrypt.key",
    {% endif %}
    "cert": "{{ setup_path }}/proxy/cert",
    "runmode": 4,
    "transitworker": 6,
    "level": "error",
    "bizid": {{ bk_supplier_id }},
    "cloudid": {{ bk_cloud_id }},
    "dataserver": [
        {% for gse_outer_ip in dataserver_outer_ips%}
            {
                "ip": "{{ gse_outer_ip }}",
                "port": {{ data_port }}
            }{% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "transitserver": [
        {"ip": "{{ inner_ip }}", "port": {{ data_port }}}
    ]
}"""


def generate_gse_config(bk_cloud_id, filename, node_type, inner_ip):
    host = Host.objects.get(bk_cloud_id=bk_cloud_id, inner_ip=inner_ip)
    agent_config = host.agent_config
    setup_path = agent_config["setup_path"]
    log_path = agent_config["log_path"]
    data_path = agent_config["data_path"]

    taskserver_outer_ips = [server["outer_ip"] for server in host.ap.taskserver]
    btfileserver_outer_ips = [server["outer_ip"] for server in host.ap.btfileserver]
    dataserver_outer_ips = [server["outer_ip"] for server in host.ap.dataserver]

    if host.os_type == constants.OsType.WINDOWS:
        path_sep = constants.WINDOWS_SEP
        dataipc = agent_config.get("dataipc", 47000)
    else:
        path_sep = constants.LINUX_SEP
        dataipc = agent_config.get("dataipc", "/var/run/ipc.state.report")

    template = {}
    context = {}
    port_config = host.ap.port_config
    if node_type in ["agent", "pagent"]:
        template = AGENT_TEMPLATE
        # 路径使用json.dumps 主要是为了解决Windows路径，如 C:\gse —> C:\\gse

        password_keyfile = path_sep.join([setup_path, "agent", "cert", "cert_encrypt.key"])
        cert = path_sep.join([setup_path, "agent", "cert"])
        proccfg = path_sep.join([setup_path, "agent", "etc", "procinfo.json"])
        procgroupcfg = path_sep.join([setup_path, "agent", "etc", "procgroupinfo.json"])
        alarmcfgpath = path_sep.join([setup_path, "plugins", "etc"])
        if host.os_type.lower() == "windows":
            setup_path = json.dumps(setup_path)
            log_path = json.dumps(log_path)
            password_keyfile = json.dumps(password_keyfile)
            cert = json.dumps(cert)
            proccfg = json.dumps(proccfg)
            procgroupcfg = json.dumps(procgroupcfg)
            alarmcfgpath = json.dumps(alarmcfgpath)
        else:
            setup_path = f'"{setup_path}"'
            log_path = f'"{log_path}"'
            password_keyfile = f'"{password_keyfile}"'
            cert = f'"{cert}"'
            proccfg = f'"{proccfg}"'
            procgroupcfg = f'"{procgroupcfg}"'
            alarmcfgpath = f'"{alarmcfgpath}"'
            dataipc = f'"{dataipc}"'

        context = {
            "setup_path": setup_path,
            "log_path": log_path,
            "agentip": inner_ip,
            "bk_supplier_id": 0,
            "bk_cloud_id": bk_cloud_id,
            "default_cloud_id": constants.DEFAULT_CLOUD,
            "identityip": inner_ip,
            "region_id": host.ap.region_id,
            "city_id": host.ap.city_id,
            "password_keyfile": False if settings.BKAPP_RUN_ENV == constants.BkappRunEnvType.ce else password_keyfile,
            "cert": cert,
            "proccfg": proccfg,
            "procgroupcfg": procgroupcfg,
            "alarmcfgpath": alarmcfgpath,
            "dataipc": dataipc,
            "zkhost": ",".join(f'{zk_host["zk_ip"]}:{zk_host["zk_port"]}' for zk_host in host.ap.zk_hosts),
            "zkauth": f"{host.ap.zk_account}:{host.ap.zk_password}",
            "proxy_servers": [proxy.inner_ip for proxy in host.proxies],
            "peer_exchange_switch_for_agent": host.extra_data.get("peer_exchange_switch_for_agent", 1),
            "bt_speed_limit": host.extra_data.get("bt_speed_limit"),
            "io_port": port_config.get("io_port"),
            "file_svr_port": port_config.get("file_svr_port"),
            "trunk_port": port_config.get("trunk_port"),
            "db_proxy_port": port_config.get("db_proxy_port"),
            "data_port": port_config.get("data_port"),
            "bt_port_start": port_config.get("bt_port_start"),
            "bt_port_end": port_config.get("bt_port_end"),
            "agent_thrift_port": port_config.get("agent_thrift_port"),
            "api_server_port": port_config.get("api_server_port"),
            "proc_port": port_config.get("proc_port"),
        }

    if node_type == "proxy":
        # proxy 只能是Linux机器
        template = {"btsvr.conf": BTSVR_TEMPLATE, "agent.conf": PROXY_TEMPLATE, "transit.conf": TRANSIT_TEMPLATE}[
            filename
        ]

        context = {
            "password_keyfile": False if settings.BKAPP_RUN_ENV == constants.BkappRunEnvType.ce else True,
            "setup_path": setup_path,
            "log_path": log_path,
            "data_path": data_path,
            "bk_supplier_id": 0,
            "bk_cloud_id": bk_cloud_id,
            "taskserver_outer_ips": taskserver_outer_ips,
            "btfileserver_outer_ips": btfileserver_outer_ips,
            "dataserver_outer_ips": dataserver_outer_ips,
            "inner_ip": inner_ip,
            "outer_ip": host.outer_ip,
            "proxy_servers": [inner_ip],
            "region_id": host.ap.region_id,
            "city_id": host.ap.city_id,
            "dataipc": dataipc,
            "peer_exchange_switch_for_agent": host.extra_data.get("peer_exchange_switch_for_agent", 1),
            "bt_speed_limit": host.extra_data.get("bt_speed_limit"),
            "io_port": port_config.get("io_port"),
            "file_svr_port": port_config.get("file_svr_port"),
            "data_port": port_config.get("data_port"),
            "bt_port_start": port_config.get("bt_port_start"),
            "bt_port_end": port_config.get("bt_port_end"),
            "btsvr_thrift_port": port_config.get("btsvr_thrift_port"),
            "bt_port": port_config.get("bt_port"),
            "tracker_port": port_config.get("tracker_port"),
        }

    return nested_render_data(template, context)


@login_exempt
@csrf_exempt
def get_gse_config(request):
    """
    @api {POST} /get_gse_config/ 获取配置
    @apiName get_gse_config
    @apiGroup subscription
    """
    data = json.loads(request.body)

    bk_cloud_id = int(data.get("bk_cloud_id"))
    filename = data.get("filename")
    node_type = data.get("node_type")
    inner_ip = data.get("inner_ip")
    token = data.get("token")

    decrypted_token = _decrypt_token(token)
    if inner_ip != decrypted_token["inner_ip"] or bk_cloud_id != decrypted_token["bk_cloud_id"]:
        logger.error(
            "token[{token}] 非法, 请求参数为: {data}, token解析为: {decrypted_token}".format(
                token=token, data=data, decrypted_token=decrypted_token
            )
        )
        raise PermissionError("what are you doing?")

    config = generate_gse_config(bk_cloud_id, filename, node_type, inner_ip)

    return HttpResponse(config)


@login_exempt
@csrf_exempt
def report_log(request):
    """
    @api {POST} /report_log/ 上报日志
    @apiName report_log
    @apiGroup subscription
    @apiParam {object} request
    @apiParamExample {Json} 请求参数
    {
        "task_id": "node_id",
        "token": "",
        "logs": [
            {
                "timestamp": "1580870937",
                "level": "INFO",
                "step": "check_deploy_result",
                "log": "gse agent has been deployed successfully",
                "status": "DONE"
            }
        ]
    }
    """
    data = json.loads(request.body)
    logger.info(f"[report_log]: {request.body}")

    token = data.get("token")
    decrypted_token = _decrypt_token(token)

    if decrypted_token.get("task_id") != data["task_id"]:
        logger.error(f"token[{token}] 非法, task_id为:{data['task_id']}, token解析为: {decrypted_token}")
        raise PermissionError("what are you doing?")

    task_service.callback(data["task_id"], data["logs"])
    return JsonResponse({})


def _decrypt_token(token: str) -> dict:
    """
    解析token
    """
    try:
        token_decrypt = aes_cipher.decrypt(token)
    except Exception as err:
        logger.error(f"{token}解析失败")
        raise err

    inner_ip, bk_cloud_id, task_id, timestamp = token_decrypt.split("|")
    return_value = {
        "inner_ip": inner_ip,
        "bk_cloud_id": int(bk_cloud_id),
        "task_id": task_id,
        "timestamp": timestamp,
    }
    # timestamp 超过1小时，认为是非法请求
    if time.time() - float(timestamp) > 3600:
        logger.error(f"token[{token}] 非法, timestamp超时不符合预期, {return_value}")
        raise PermissionError("what are you doing?")

    return return_value
