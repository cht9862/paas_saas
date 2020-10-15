# -*- coding: utf-8 -*-

import hashlib
import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.utils import timezone

from apps.utils.batch_request import batch_request
from apps.backend.constants import TargetNodeType
from apps.backend.subscription.errors import ConfigRenderFailed, PipelineTreeParseError
from apps.backend.utils.pipeline_parser import PipelineParser
from apps.component.esbclient import client_v2
from apps.exceptions import ComponentCallError
from apps.node_man import constants
from apps.utils.basic import chunk_lists
from apps.node_man.models import Host, Job, JobTask, SubscriptionInstanceRecord, Packages

logger = logging.getLogger("app")

client_v2.backend = True


def create_group_id(subscription, instance):
    """
    创建插件组ID
    """
    if subscription.object_type == subscription.ObjectType.SERVICE:
        # 服务实例
        instance_id = instance["service"]["id"]
    else:
        # 主机实例
        instance_id = instance["host"]["bk_host_id"]
    group_id = "sub_{subscription_id}_{object_type}_{instance_id}".format(
        subscription_id=subscription.id, object_type=subscription.object_type.lower(), instance_id=instance_id,
    )
    return group_id


def parse_group_id(group_id):
    """
    解析group id
    """
    source_type, subscription_id, object_type, _id = group_id.split("_")
    return {
        "subscription_id": subscription_id,
        "object_type": object_type,
        "id": _id,
    }


def create_topo_node_id(topo_node):
    return "{}|{}".format(topo_node["bk_obj_id"], topo_node["bk_inst_id"])


def get_module_to_topo_dict(bk_biz_id):
    topo_tree = client_v2.cc.search_biz_inst_topo({"bk_username": "admin", "bk_biz_id": bk_biz_id})

    node_relations = {}

    queue = topo_tree
    while queue:
        topo_node = queue.pop()
        topo_node_id = create_topo_node_id(topo_node)

        if topo_node_id not in node_relations:
            node_relations[topo_node_id] = [topo_node_id]

        queue.extend(topo_node["child"])
        for child in topo_node["child"]:
            child_node_id = create_topo_node_id(child)
            node_relations[child_node_id] = node_relations[topo_node_id] + [child_node_id]

    return {
        topo_node_id: node_relations[topo_node_id]
        for topo_node_id in node_relations
        if topo_node_id.startswith("module")
    }


def create_node_id(data):
    """
    转换成字符串格式的node_id
    :param data: dict
    {
        "object_type": "HOST",
        "node_type": "TOPO",
        "bk_obj_id": "set",
        "bk_inst_id": 123
    }
    {
        "object_type": "SERVICE",
        "node_type": "INSTANCE",
        "service_instance_id": 123
    }
    {
        "object_type": "HOST",
        "node_type": "INSTANCE",
        "bk_host_id": 1213
    }
    :return: str
    """
    if data["node_type"] == "INSTANCE":
        _type = data["object_type"].lower()
        if _type == "host":
            _id = create_host_key(data)
        else:
            _id = data["id"]
    else:
        _type = data["bk_obj_id"]
        _id = data["bk_inst_id"]

    return "{object_type}|{node_type}|{type}|{id}".format(
        object_type=data["object_type"].lower(), node_type=data["node_type"].lower(), type=_type, id=_id,
    )


def parse_node_id(node_id):
    object_type, node_type, _type, _id = node_id.split("|")

    return {
        "object_type": object_type,
        "node_type": node_type,
        "type": _type,
        "id": _id,
    }


def parse_host_key(host_key):
    """
    :param host_key:  三段式：10.1.1.10-0-tencent  或者 1024
    :return:
    """
    try:
        ip, bk_could_id, bk_supplier_id = host_key.split("-")
    except ValueError:
        return {"bk_host_id": int(host_key)}
    else:
        return {"ip": ip, "bk_cloud_id": bk_could_id, "bk_supplier_id": bk_supplier_id}


def create_host_key(data):
    """
    根据ip，bk_cloud_id，bk_supplier_id生成key
    :param data: dict
    :return: str
    """

    if "bk_host_id" in data:
        return data["bk_host_id"]

    if isinstance(data["bk_cloud_id"], list):
        if data["bk_cloud_id"]:
            bk_cloud_id = data["bk_cloud_id"][0]["bk_inst_id"]
        else:
            bk_cloud_id = constants.DEFAULT_CLOUD
    else:
        bk_cloud_id = data["bk_cloud_id"]

    return "{}-{}-{}".format(data.get("bk_host_innerip") or data.get("ip"), bk_cloud_id, constants.DEFAULT_SUPPLIER_ID)


def get_host_by_inst(bk_biz_id, inst_list):
    """
    根据拓扑节点查询主机
    :param inst_list: 实例列表
    :param bk_biz_id: 业务ID
    :return: dict 主机信息
    """
    hosts = []
    for inst in inst_list:
        params = {"bk_username": "admin", "condition": []}
        if bk_biz_id:
            params["bk_biz_id"] = str(bk_biz_id)

        if inst["bk_obj_id"] != "biz":
            if inst["bk_obj_id"] in ["module", "set"]:
                field = "bk_{obj}_id".format(obj=inst["bk_obj_id"])
            else:
                field = "bk_inst_id"

            params["condition"].append(
                {
                    "bk_obj_id": inst["bk_obj_id"],
                    "fields": [],
                    "condition": [{"field": field, "operator": "$eq", "value": inst["bk_inst_id"]}],
                }
            )
        else:
            params["condition"].append(
                {
                    "bk_obj_id": "biz",
                    "fields": [],
                    "condition": [{"field": "bk_biz_id", "operator": "$eq", "value": inst["bk_inst_id"]}],
                }
            )

        if inst["bk_obj_id"] != "module":
            params["condition"].append({"bk_obj_id": "module", "fields": [], "condition": []})

        result = client_v2.cc.search_host(params)
        for host in result["info"]:
            _host = host["host"]
            _host["module"] = host["module"]

            if isinstance(_host["bk_cloud_id"], list):
                if _host["bk_cloud_id"]:
                    _host["bk_cloud_id"] = _host["bk_cloud_id"][0]["bk_inst_id"]
                else:
                    _host["bk_cloud_id"] = constants.DEFAULT_CLOUD
            if host.get("biz", []):
                _host["bk_biz_id"] = host["biz"][0]["bk_biz_id"]
                _host["bk_biz_name"] = host["biz"][0]["bk_biz_name"]
            hosts.append(_host)

    return hosts


def get_process_by_host_id(bk_biz_id):
    try:
        params = {"bk_biz_id": int(bk_biz_id), "with_name": True}
        result = batch_request(client_v2.cc.get_service_instances_detail, params)
    except (TypeError, ComponentCallError):
        logger.warning(f"Failed to get_service_instances_detail with biz_id={bk_biz_id}")
        service_instances = []
    else:
        service_instances = result

    host_processes = defaultdict(dict)

    for service_instance in service_instances:
        for process in service_instance.get("process_instances") or []:
            process["process"].update(process["relation"])
            bk_host_id = process["relation"]["bk_host_id"]
            bk_func_name = process["process"]["bk_func_name"]
            host_processes[bk_host_id][bk_func_name] = process["process"]

    return host_processes


def get_service_instance_by_inst(bk_biz_id, inst_list):
    module_ids = set()
    no_module_inst_list = set()
    # 先查询出模块
    for inst in inst_list:
        if inst["bk_obj_id"] == "module":
            module_ids.add(int(inst["bk_inst_id"]))
        else:
            no_module_inst_list.add(create_topo_node_id(inst))

    module_to_topo = get_module_to_topo_dict(bk_biz_id)
    for module_node_id in module_to_topo:
        if set(module_to_topo[module_node_id]).intersection(no_module_inst_list):
            module_ids.add(int(module_node_id.split("|")[1]))

    params = {"bk_biz_id": int(bk_biz_id), "with_name": True}

    service_instances = batch_request(client_v2.cc.get_service_instances_detail, params)

    service_instances = [
        service_instance for service_instance in service_instances if service_instance["bk_module_id"] in module_ids
    ]

    return service_instances


def get_service_instance_by_ids(bk_biz_id, ids):
    """
    根据服务实例id获取服务实例详情
    :param bk_biz_id: int 业务id
    :param ids: list 服务实例id
    :return:
    """
    params = {
        "bk_biz_id": int(bk_biz_id),
        "with_name": True,
        "service_instance_ids": ids,
    }

    result = batch_request(client_v2.cc.get_service_instances_detail, params)
    return result


def get_host_detail_by_template(template_info_list: list, bk_biz_id: int = None):
    """
    根据集群模板ID/服务模板ID获得主机的详细信息
    :param template_info_list: 模板信息列表
    :param bk_biz_id: 业务ID
    :return: 主机列表信息
    """
    if not template_info_list:
        return []

    fields = (
        "bk_host_innerip",
        "bk_cloud_id",
        "bk_host_id",
        "bk_biz_id",
        "bk_host_outerip",
        "bk_host_name",
        "bk_os_name",
        "bk_os_type",
        "operator",
        "bk_bak_operator",
        "bk_state_name",
        "bk_isp_name",
        "bk_province_name",
        "bk_supplier_account",
        "bk_state",
        "bk_os_version",
        "bk_state",
    )

    # 每次只能选择单独一种目标节点类型
    bk_obj_id = template_info_list[0]["bk_obj_id"]

    if bk_obj_id == TargetNodeType.SERVICE_TEMPLATE:
        # 服务模板
        call_func = client_v2.cc.find_host_by_service_template
        template_ids = [info["bk_inst_id"] for info in template_info_list]
    else:
        # 集群模板
        call_func = client_v2.cc.find_host_by_set_template
        template_ids = [info["bk_inst_id"] for info in template_info_list]

    host_info_result = batch_request(
        call_func, dict(bk_service_template_ids=template_ids, bk_biz_id=bk_biz_id, fields=fields)
    )

    return host_info_result


def get_service_instances_by_template(template_info_list: list, bk_biz_id: int = None):
    """
    根据集群模板ID/服务模板ID获得服务实例列表
    :param template_info_list: 模板信息列表
    :param bk_biz_id: 业务ID
    :return: 服务实例列表
    """
    if not template_info_list:
        return []

    # 每次只能选择单独一种目标节点类型
    bk_obj_id = template_info_list[0]["bk_obj_id"]

    params = {"bk_biz_id": int(bk_biz_id), "with_name": True}
    if bk_obj_id == TargetNodeType.SERVICE_TEMPLATE:
        # 服务模板下的服务实例
        params["bk_service_template_ids"] = [info["bk_inst_id"] for info in template_info_list]
        service_instances = batch_request(client_v2.cc.get_service_instances_detail, params)
    else:
        # 集群模板下的服务实例
        call_func = client_v2.cc.find_host_by_set_template
        template_ids = [info["bk_inst_id"] for info in template_info_list]
        host_info_result = batch_request(
            call_func, dict(bk_service_template_ids=template_ids, bk_biz_id=int(bk_biz_id), fields=("bk_host_id"))
        )
        bk_host_ids = [inst["bk_host_id"] for inst in host_info_result]
        all_service_instances = batch_request(client_v2.cc.get_service_instances_detail, params)
        service_instances = [instance for instance in all_service_instances if instance["bk_host_id"] in bk_host_ids]

    return service_instances


def get_host_detail(host_info_list: list, bk_biz_id: int = None):
    """
    获取主机详情
    :param bk_biz_id: 业务ID
    :param host_info_list: list 主机部分信息
    # 两种主机格式只能取其中一种
    [{
        "ip": "127.0.0.1",
        "bk_cloud_id": "0",
        "bk_supplier_id": "0"
    },
    # 或者
    {
        "bk_host_id": 1
    }]
    :return: list 主机详细信息
    """
    if not host_info_list:
        return []

    host_details = []

    search_host_params = {"bk_username": "admin", "condition": []}

    # 仅支持一种主机格式
    first_host_info = host_info_list[0]
    if "instance_info" in first_host_info:
        # 当已存在instance_info时，不到 CMDB 查询，用于新安装AGENT的场景
        return [host.get("instance_info", {}) for host in host_info_list]
    if "bk_host_id" in first_host_info:
        search_host_params["condition"].append(
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": [
                    {
                        "field": "bk_host_id",
                        "operator": "$in",
                        "value": [host["bk_host_id"] for host in host_info_list],
                    }
                ],
            }
        )

    elif "ip" in first_host_info and "bk_cloud_id" in first_host_info:
        search_host_params["condition"].append(
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": [
                    {"field": "bk_host_innerip", "operator": "$in", "value": [host["ip"] for host in host_info_list]}
                ],
            }
        )

    search_host_params["condition"].append(
        {
            "bk_obj_id": "biz",
            "fields": ["bk_biz_id", "bk_biz_name"],
            "condition": [{"field": "bk_biz_id", "operator": "$eq", "value": bk_biz_id}] if bk_biz_id else [],
        }
    )

    result = client_v2.cc.search_host(search_host_params)

    host_key_dict = {}
    host_id_dict = {}
    for host_info in result["info"]:
        _host = host_info["host"]
        if isinstance(_host["bk_cloud_id"], list) and _host["bk_cloud_id"]:
            host_info["host"]["bk_cloud_name"] = _host["bk_cloud_id"][0]["bk_inst_name"]
            host_info["host"]["bk_cloud_id"] = _host["bk_cloud_id"][0]["bk_inst_id"]
        if host_info["biz"]:
            host_info["host"]["bk_biz_id"] = host_info["biz"][0]["bk_biz_id"]
            host_info["host"]["bk_biz_name"] = host_info["biz"][0]["bk_biz_name"]
        host_key = f'{_host["bk_host_innerip"]}-{_host["bk_cloud_id"]}-{constants.DEFAULT_SUPPLIER_ID}'
        host_key_dict[host_key] = _host
        host_id_dict[_host["bk_host_id"]] = _host

    for host_info in host_info_list:
        if "bk_host_id" in host_info:
            if host_info["bk_host_id"] in host_id_dict:
                host_details.append(host_id_dict[host_info["bk_host_id"]])
        else:
            host_key = create_host_key(host_info)
            if host_key in host_key_dict:
                host_details.append(host_key_dict[host_key])

    return host_details


def add_host_module_info(host_biz_relations, instances):
    """
    增加主机的模块信息（为降低圈复杂度所写）
    :param host_biz_relations: 主机的业务相关信息
    :param instances: 目标信息，模块信息将保存到这里
    :return: instances
    """

    bk_host_module_map_id = {}
    for relation in host_biz_relations:
        if relation["bk_host_id"] not in bk_host_module_map_id:
            bk_host_module_map_id[relation["bk_host_id"]] = [{"bk_module_id": relation["bk_module_id"]}]
        else:
            bk_host_module_map_id[relation["bk_host_id"]].append({"bk_module_id": relation["bk_module_id"]})

    for instance in instances:
        if "module" not in instance["host"]:
            instance["host"]["module"] = bk_host_module_map_id.get(instance["host"]["bk_host_id"])
    return instances


def get_instances_by_scope(scope):
    """
    获取范围内的所有主机
    :param scope: dict {
        "bk_biz_id": 2,
        "object_type": "SERVICE",
        "node_type": "TOPO",
        "need_register": False, // 是否需要注册到CMDB
        "nodes": [
            // SERVICE-INSTANCE 待补充
            // HOST-TOPO
            {
                "bk_inst_id": 33,   // 节点实例ID
                "bk_obj_id": "module",  // 节点对象ID
            },
            // HOST-INSTANCE
            {
                "ip": "10.0.0.1",
                "bk_cloud_id": 0,
                "bk_supplier_id": 0,
                "instance_info": {}  // 注册到CMDB的主机信息
            },
            {
                'bk_host_id': 1,
            }
        ]
    }
    :return: dict {
        "host|instance|host|xxxx": {...},
        "host|instance|host|yyyy": {...},
    }
    """
    instances = []
    bk_biz_id = scope["bk_biz_id"]
    nodes = scope["nodes"]
    need_register = scope.get("need_register", False)

    # 按照拓扑查询
    if scope["node_type"] == "TOPO":
        if scope["object_type"] == "HOST":
            instances.extend([{"host": inst} for inst in get_host_by_inst(bk_biz_id, nodes)])
        else:
            # 补充服务实例中的信息
            instances.extend([{"service": inst} for inst in get_service_instance_by_inst(bk_biz_id, nodes)])

    # 按照实例查询
    elif scope["node_type"] == "INSTANCE":
        if scope["object_type"] == "HOST":
            instances.extend([{"host": inst} for inst in get_host_detail(nodes, bk_biz_id=bk_biz_id)])
        else:
            service_instance_ids = [int(node["id"]) for node in nodes]
            instances.extend(
                [{"service": inst} for inst in get_service_instance_by_ids(bk_biz_id, service_instance_ids)]
            )

    # 按照模板查询
    elif scope["node_type"] in [TargetNodeType.SERVICE_TEMPLATE, TargetNodeType.SET_TEMPLATE]:
        if scope["object_type"] == "HOST":
            # 补充实例所属模块ID
            host_biz_relations = []
            instances.extend([{"host": inst} for inst in get_host_detail_by_template(nodes, bk_biz_id=bk_biz_id)])
            bk_host_id_chunks = chunk_lists([instance["host"]["bk_host_id"] for instance in instances], 500)
            with ThreadPoolExecutor(max_workers=settings.CONCURRENT_NUMBER) as ex:
                tasks = [
                    ex.submit(client_v2.cc.find_host_biz_relations, dict(bk_host_id=chunk, bk_biz_id=bk_biz_id))
                    for chunk in bk_host_id_chunks
                ]
                for future in as_completed(tasks):
                    host_biz_relations.extend(future.result())

            instances = add_host_module_info(host_biz_relations, instances)
        else:
            instances.extend(
                [{"service": inst} for inst in get_service_instances_by_template(nodes, bk_biz_id=bk_biz_id)]
            )

    module_to_topo = {}
    if not need_register:
        # 补全实例主机信息
        if scope["object_type"] == "SERVICE":
            host_dict = {
                host_info["bk_host_id"]: host_info
                for host_info in get_host_detail([instance["service"] for instance in instances], bk_biz_id=bk_biz_id)
            }
            for instance in instances:
                instance["host"] = host_dict[instance["service"]["bk_host_id"]]

        # 补全scope信息
        try:
            module_to_topo = get_module_to_topo_dict(scope["bk_biz_id"])
        except Exception:
            logger.warning(f'module_to_topo查询失败 biz:{scope["bk_biz_id"]}')

        for instance in instances:
            if scope["node_type"] == "INSTANCE":
                if scope["object_type"] == "HOST":
                    host = instance["host"]
                    instance["scope"] = [
                        {
                            "ip": host["bk_host_innerip"],
                            "bk_cloud_id": host["bk_cloud_id"],
                            "bk_supplier_id": constants.DEFAULT_SUPPLIER_ID,
                        }
                    ]
                else:
                    instance["scope"] = [{"service_instance_id": instance["service"]["id"]}]
            else:
                instance_scope = []
                if scope["object_type"] == "HOST":
                    module_ids = [module["bk_module_id"] for module in instance["host"]["module"]]
                else:
                    module_ids = [instance["service"]["bk_module_id"]]

                for topo_node in scope["nodes"]:
                    topo_node_id = create_topo_node_id(topo_node)
                    for module_id in module_ids:
                        module_node_id = create_topo_node_id({"bk_obj_id": "module", "bk_inst_id": module_id})
                        if topo_node_id in module_to_topo.get(module_node_id, []):
                            instance_scope.append(topo_node)

                instance["scope"] = instance_scope

        # 补全process信息
        if scope["object_type"] == "HOST":
            host_processes = get_process_by_host_id(bk_biz_id)
            for instance in instances:
                bk_host_id = instance["host"]["bk_host_id"]
                instance["process"] = host_processes[bk_host_id]
                # 补全字段
                instance["service"] = None
        else:
            for instance in instances:
                processes = {}
                for process in instance["service"].get("process_instances") or []:
                    processes[process["process"]["bk_process_name"]] = process["process"]
                instance["process"] = processes

                del instance["service"]["process_instances"]

    instances_dict = {}
    data = {
        "object_type": scope["object_type"],
        "node_type": "INSTANCE",
    }
    for instance in instances:
        if data["object_type"] == "HOST":
            data.update(instance["host"])
        else:
            data.update(instance["service"])
        instances_dict[create_node_id(data)] = instance

    return instances_dict


def get_all_subscription_steps_context(subscription_step, instance_info, target_host, plugin_name):
    """
    获取订阅步骤上下文数据
    :param SubscriptionStep subscription_step: 订阅ID
    :param dict instance_info: 实例信息
    :param dict target_host: 主机信息
    :param string plugin_name: 插件名称
    :return:
    """
    from apps.backend.subscription.steps import StepFactory

    context = {}
    all_step_data = {
        step.step_id: StepFactory.get_step_manager(step).get_step_data(instance_info, target_host)
        for step in subscription_step.subscription.steps
    }
    host = Host.get_by_host_info(instance_info["host"])
    agent_config = host.ap.agent_config[host.os_type.lower()]
    setup_path = agent_config["setup_path"]
    log_path = agent_config["log_path"]
    run_path = agent_config.get("run_path")
    data_path = agent_config["data_path"]
    if host.os_type == constants.OsType.WINDOWS:
        path_sep = constants.WINDOWS_SEP
        dataipc = agent_config.get("dataipc", 47000)
        host_id = agent_config.get("host_id", "C:\\gse\\data\\host\\hostid")
        endpoint = "127.0.0.1:{}".format(dataipc)
    else:
        path_sep = constants.LINUX_SEP
        endpoint = agent_config.get("dataipc", "/var/run/ipc.state.report")
        host_id = agent_config.get("host_id", "/var/lib/gse/host/hostid")

    plugin_path = {
        "log_path": log_path,
        "data_path": data_path,
        "pid_path": run_path or log_path,
        "setup_path": setup_path,
        "endpoint": endpoint,
        "host_id": host_id,
        "subconfig_path": path_sep.join([setup_path, "plugins", "etc", plugin_name]),
    }
    # 当前step_id的数据单独拎出来，作为 shortcut
    context.update(all_step_data[subscription_step.step_id])
    context.update(cmdb_instance=instance_info, step_data=all_step_data, target=instance_info, plugin_path=plugin_path)
    return context


def render_config_files(config_templates, host_status, context):
    """
    根据订阅配置及步骤信息渲染配置模板
    :param list[PluginConfigInstance] config_templates: 配置文件模板
    :param HostStatus host_status: 主机进程信息
    :param dict context: 上下文信息
    :return: example: [
        {
            "instance_id": config.id,
            "content": content,
            "file_path": config.template.file_path,
            "md5": md5sum,
            "name": "xxx"
        }
    ]
    """
    package_obj = Packages.objects.filter(
        project=host_status.name,
        os=host_status.host.os_type.lower(),
        cpu_arch__in=[constants.CpuType.x86_64, constants.CpuType.powerpc],
    ).last()
    rendered_configs = []
    for config in config_templates:
        try:
            content = config.render_config_template(context)
        except Exception as e:
            raise ConfigRenderFailed({"name": config.template.name, "msg": e})
        # 计算配置文件的MD5
        md5 = hashlib.md5()
        md5.update(content.encode())
        md5sum = md5.hexdigest()

        rendered_config = {
            "instance_id": config.id,
            "content": content,
            "file_path": config.template.file_path,
            "md5": md5sum,
        }
        if package_obj and package_obj.plugin_desc.is_official and not config.template.is_main:
            # 官方插件的部署方式为单实例多配置，在配置模板的名称上追加 group id 即可对配置文件做唯一标识
            filename, extension = os.path.splitext(config.template.name)
            rendered_config["name"] = "{filename}_{group_id}{extension}".format(
                filename=filename, group_id=host_status.group_id, extension=extension
            )
        else:
            # 非官方插件、官方插件中的主配置文件，无需追加 group id
            rendered_config["name"] = config.template.name

        rendered_configs.append(rendered_config)
    return rendered_configs


def get_subscription_task_instance_status(instance_record, pipeline_parser, need_detail=False):
    """
    :param instance_record:
    :param PipelineParser pipeline_parser:
    :param need_detail: 是否需要详细信息
    :return:
    """
    # 解析 pipeline 任务树
    try:
        instance_tree = pipeline_parser.sorted_pipeline_tree[instance_record.pipeline_id]
        steps_tree = instance_tree["children"]
    except KeyError:
        raise PipelineTreeParseError()

    # 新创建的记录会覆盖前面的实例执行记录
    instance_status = {
        "task_id": instance_record.task_id,
        "instance_id": instance_record.instance_id,
        "create_time": instance_record.create_time,
        "pipeline_id": instance_record.pipeline_id,
    }

    # 是否返回详细信息
    if need_detail:
        instance_status.update({"instance_info": instance_record.instance_info})
    else:
        instance_status.update({"instance_info": instance_record.simple_instance_info()})

    # 更新 Instance Pipeline 状态信息
    instance_status.update(pipeline_parser.get_node_state(instance_record.pipeline_id))

    # 更新 Step Pipeline 状态信息
    all_steps_info = instance_record.get_all_step_data()

    # 过滤未执行的步骤
    steps_info = [step for step in all_steps_info if step["pipeline_id"]]
    for step in steps_info:
        step.update(pipeline_parser.get_node_state(step["pipeline_id"]))
        try:
            if not step["pipeline_id"]:
                # 没有代表不执行该节点
                continue
            single_step_tree = steps_tree[step["pipeline_id"]]
            hosts_tree = list(single_step_tree["children"].values())[0]["children"]
        except Exception:
            raise PipelineTreeParseError()
        step["node_name"] = single_step_tree["name"]

        # 更新 target_host 信息
        step["target_hosts"] = []
        for host_tree in list(hosts_tree.values()):
            target_host_info = {
                "pipeline_id": host_tree["id"],
                "node_name": host_tree["name"],
                "sub_steps": [],
            }
            target_host_info.update(pipeline_parser.get_node_state(host_tree["id"]))

            # 更新 target_host 每个子步骤信息
            for single_host_step in list(host_tree["children"].values()):
                sub_step = {
                    "pipeline_id": single_host_step["id"],
                    "index": single_host_step["index"],
                    "node_name": single_host_step["name"],
                }
                sub_step.update(pipeline_parser.get_node_state(single_host_step["id"]))

                if need_detail:
                    sub_step.update(pipeline_parser.get_node_data(single_host_step["id"]))
                    log = pipeline_parser.get_node_log(single_host_step["id"])
                    if sub_step["ex_data"]:
                        log = f"{log}\n{sub_step['ex_data']}"
                    sub_step.update(log=log)

                target_host_info["sub_steps"].append(sub_step)
                target_host_info["sub_steps"].sort(key=lambda i: i["index"])

            step["target_hosts"].append(target_host_info)

    instance_status["steps"] = steps_info

    return instance_status


def update_job_status(pipeline_id, result=None):
    logger.info(f"start_updating_job_status: {pipeline_id}")
    subscription_instance = SubscriptionInstanceRecord.objects.get(pipeline_id=pipeline_id)

    try:
        job = Job.objects.get(subscription_id=subscription_instance.subscription_id,)
    except Job.DoesNotExist:
        logger.warning(f"订阅任务({subscription_instance.subscription_id}不存在)")
        return
    # if job.statistics['running_count'] <= 0:
    #     return

    instance_records = SubscriptionInstanceRecord.objects.filter(
        subscription_id=subscription_instance.subscription_id, is_latest=True
    ).order_by("id")
    # 去重
    instances_dict = {instance_record.instance_id: instance_record for instance_record in instance_records}
    instance_records = instances_dict.values()

    pipeline_ids = [r.pipeline_id for r in instance_records]

    pipeline_parser = PipelineParser(pipeline_ids)

    success_count = 0
    failed_count = 0
    running_count = 0
    pending_count = 0

    for instance_record in instance_records:
        status = get_subscription_task_instance_status(instance_record, pipeline_parser)["status"]
        if instance_record.pipeline_id == pipeline_id:
            # 查询状态时，此pipeline还未结算，因此需要根据result把本pipeline也进行结算
            if result is False:
                status = constants.JobStatusType.FAILED
            elif result is True:
                status = constants.JobStatusType.SUCCESS

            host = Host.get_by_host_info(instance_record.instance_info["host"])
            JobTask.objects.filter(bk_host_id=host.bk_host_id).update(status=status)

        if status == constants.JobStatusType.SUCCESS:
            success_count += 1
        elif status == constants.JobStatusType.FAILED:
            failed_count += 1
        elif status == constants.JobStatusType.RUNNING:
            running_count += 1
        else:
            pending_count += 1

    if running_count + pending_count == 0:
        # 所有IP都被执行完毕
        if failed_count == 0:
            job.status = constants.JobStatusType.SUCCESS
        elif success_count == 0:
            job.status = constants.JobStatusType.FAILED
        else:
            job.status = constants.JobStatusType.PART_FAILED
        job.end_time = timezone.now()

    job.statistics.update(
        {"success_count": success_count, "failed_count": failed_count, "running_count": running_count}
    )
    job.save(update_fields=["statistics", "status", "end_time"])
    logger.info(f"end_updating_job_status: {pipeline_id}")
