# -*- coding: utf-8 -*-
import base64
import re

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from apps.node_man import constants as const
from apps.node_man.constants import IamActionType
from apps.node_man.exceptions import (
    AliveProxyNotExistsError,
    AllIpFiltered,
    JobDostNotExistsError,
    JobNotPermissionError,
    MixedOperationError,
)
from apps.node_man.handlers.ap import APHandler
from apps.node_man.handlers.cloud import CloudHandler
from apps.node_man.handlers.cmdb import CmdbHandler
from apps.node_man.handlers.host import HostHandler
from apps.node_man.handlers.validator import bulk_update_validate, job_validate, operate_validator
from apps.node_man.models import Host, IdentityData, Job, JobTask
from apps.utils import APIModel
from apps.utils.basic import filter_values, suffix_slash
from common.api import NodeApi


class JobHandler(APIModel):
    def __init__(self, job_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_id = job_id

    def _get_data(self) -> Job:
        try:
            return Job.objects.get(pk=self.job_id)
        except Job.DoesNotExist:
            raise JobDostNotExistsError(_("不存在ID为{job_id}的任务").format(job_id=self.job_id))

    def ugettext_to_unicode(self, ip_filter_list: list):
        """
        针对ip_filter_list里的ugettext_lazy做字符串化的操作
        :param ip_filter_list: ip过滤列表
        :return: 格式化后的ip过滤列表
        """
        # ugettext_lazy需要转为unicode才可进行序列化
        for filter_info in ip_filter_list:
            filter_info["msg"] = str(filter_info["msg"])
        return ip_filter_list

    def check_job_permission(self, username: str, bk_biz_scope: list):
        """
        检测用户是否有当前任务的权限
        :param username: 用户名
        :param bk_biz_scope: 任务业务范围
        """
        # 检测是否有权限：拥有业务权限或创建人可以访问当前任务
        biz_info = CmdbHandler().biz_id_name({"action": IamActionType.task_history_view})
        diff = list(set(bk_biz_scope).difference(set(biz_info.keys())))
        if diff != [] and self.data.created_by != username:
            raise JobNotPermissionError(_("用户无权限访问当前任务"))

    def task_status_list(self):
        """
        返回任务执行的状态
        :return: 以Host ID为键，返回任务执行状态
        {
            bk_host_id: {
                'job_id': job_id,
                'status': status
            }
        }
        """
        task_info = {
            task["bk_host_id"]: {"status": task["status"]}
            for task in JobTask.objects.values("bk_host_id", "instance_id", "job_id", "status")
        }
        return task_info

    def check_ap_and_biz_scope(self, node_type: str, host: dict, cloud_info: dict):
        """
        返回主机的接入点、业务范围、节点类型。
        兼容订阅任务版注册<br>
        如果是非直连区域，获得该云区域下的ap_id为空<br>
        如果是直连区域，ap_id直接从参数拿, 如果是proxy，则ap_id为空<br>
        :param node_type: 节点类型
        :param host: 主机信息
        :param cloud_info: 云区域信息
        :return:
        """
        if node_type == const.NodeType.AGENT:
            if host["bk_cloud_id"] == const.DEFAULT_CLOUD:
                # 根据bk_cloud_id判断是否为AGENT
                host_ap_id = host["ap_id"]
                host_node_type = const.NodeType.AGENT
            else:
                # 根据bk_cloud_id判断是否为PAGENT
                # 如果传了ap_id优先使用传入的以适配重载配置
                host_ap_id = host.get("ap_id") or cloud_info.get(host["bk_cloud_id"], {}).get("ap_id", "")
                host_node_type = const.NodeType.PAGENT
        else:
            # PROXY
            # 如果传了ap_id优先使用传入的以适配重载配置
            host_ap_id = host.get("ap_id") or cloud_info.get(host["bk_cloud_id"], {}).get("ap_id", "")
            host_node_type = const.NodeType.PROXY

        return host_ap_id, host_node_type

    def get_commands(self, username: str, request_bk_host_id: int):
        """
        获取命令
        :param username: 用户名
        :param request_bk_host_id: 主机ID
        :return: ips_commands 每个ip的安装命令， total_commands：
        """

        job = self.data

        # 检查权限
        self.check_job_permission(username, job.bk_biz_scope)

        def gen_pre_manual_command(host, host_install_pipeline_id, batch_install):
            is_uninstall = False
            result = NodeApi.fetch_commands(
                {
                    "bk_host_id": host.bk_host_id,
                    "host_install_pipeline_id": host_install_pipeline_id[host.bk_host_id],
                    "is_uninstall": is_uninstall,
                    "batch_install": batch_install,
                }
            )
            win_commands = result["win_commands"]
            pre_commands = result["pre_commands"]
            run_cmd = result["run_cmd"]

            if isinstance(win_commands, list):
                win_commands = " & ".join(win_commands)
            if isinstance(pre_commands, list):
                pre_commands = " && ".join(pre_commands)

            manual_pre_command = (win_commands or pre_commands) + (" && " if pre_commands else " & ")
            return run_cmd, manual_pre_command

        # 云区域下的主机
        cloud_host_id = {}
        # 所有主机对应的安装步骤node_id
        host_install_pipeline_id = {}
        # 获取任务状态
        task_result = NodeApi.get_subscription_task_status(
            {"subscription_id": job.subscription_id, "task_id_list": job.task_id_list}
        )
        for result in task_result:
            bk_cloud_id = result["instance_info"]["host"]["bk_cloud_id"]
            bk_host_id = result["instance_info"]["host"].get("bk_host_id")
            if not bk_host_id:
                # 还有主机没注册成功
                return {"status": "PENDING"}

            # 获取每台主机安装任务的pipeline_id
            sub_steps = result["steps"][0]["target_hosts"][0]["sub_steps"]
            for step in sub_steps:
                if step["node_name"] == "手动安装" and (step["status"] == "RUNNING" or step["status"] == "SUCCESS"):
                    pipeline_id = step["pipeline_id"]
                    if bk_cloud_id not in cloud_host_id:
                        cloud_host_id[bk_cloud_id] = [bk_host_id]
                    else:
                        cloud_host_id[bk_cloud_id].append(bk_host_id)
                    host_install_pipeline_id[bk_host_id] = pipeline_id

        # 每个云区域下只选一个主机
        bk_host_ids = [cloud_host_id[cloud][0] for cloud in cloud_host_id]
        hosts = {host.bk_host_id: host for host in Host.objects.filter(bk_host_id__in=bk_host_ids)}

        # 所有需要安装的主机信息
        bk_host_ids = []
        for cloud in cloud_host_id:
            for host_id in cloud_host_id[cloud]:
                bk_host_ids.append(host_id)
        all_hosts = {host.bk_host_id: host for host in Host.objects.filter(bk_host_id__in=bk_host_ids)}

        commands = {}
        if request_bk_host_id == -1:
            host_to_gen = list(hosts.values())
        elif all_hosts.get(request_bk_host_id):
            host_to_gen = [all_hosts[request_bk_host_id]]
        else:
            host_to_gen = []

        for host in host_to_gen:
            # 生成命令
            batch_install = False
            # 是否为批量安装
            if len(cloud_host_id[host.bk_cloud_id]) > 1:
                batch_install = True

            run_cmd, manual_pre_command = gen_pre_manual_command(host, host_install_pipeline_id, batch_install)

            # 每个IP的单独执行命令
            ips_commands = []
            # 用于生成每个Cloud下的批量安装命令
            host_commands = []
            # 该云区域下的所有主机
            host_ids = cloud_host_id[host.bk_cloud_id]
            for host_id in host_ids:
                batch_install = False
                single_run_cmd, single_manual_pre_command = gen_pre_manual_command(
                    host, host_install_pipeline_id, batch_install
                )
                login_ip = all_hosts[host_id].login_ip
                inner_ip = all_hosts[host_id].inner_ip
                bk_cloud_id = all_hosts[host_id].bk_cloud_id
                os_type = all_hosts[host_id].os_type.lower()

                # 获得安装目标目录
                dest_dir = host.agent_config["temp_path"]
                dest_dir = suffix_slash(host.os_type.lower(), dest_dir).replace("\\", "\\\\\\\\")

                echo_pattern = (
                    '["'
                    + '","'.join(
                        [
                            login_ip or inner_ip,
                            inner_ip,
                            "<span>账号</span>",
                            "<span>端口号</span>",
                            "<span>密码/密钥</span>",
                            str(bk_cloud_id),
                            all_hosts[host_id].node_type,
                            os_type,
                            dest_dir,
                        ]
                    )
                    + '"]'
                )
                # 批量安装命令
                host_commands.append(echo_pattern)
                single_run_cmd = re.sub(r"'\[\[.*\]\]'", "'[" + echo_pattern + "]'", single_run_cmd)

                # 每个IP的单独安装命令
                ips_commands.append(
                    {
                        "ip": inner_ip,
                        "command": (single_manual_pre_command + single_run_cmd),
                        "os_type": all_hosts[host_id].os_type,
                    }
                )

            host_commands = "'[" + ",".join(host_commands) + "]'"
            host_commands = re.sub(r"'\[\[.*\]\]'", host_commands, run_cmd)

            commands[host.bk_cloud_id] = {
                "ips_commands": ips_commands,
                "total_commands": (manual_pre_command + host_commands),
            }

        return commands

    def list(self, params: dict, username: str):
        """
        Job 任务历史列表
        :param params: 请求参数的字典
        :param username: 用户名
        """

        kwargs = {
            "job_type__in": params.get("job_type"),
            "status__in": params.get("status"),
            "created_by__in": params.get("created_by"),
            "id__in": params.get("job_id"),
        }

        # 获得业务id与名字的映射关系(用户有权限获取的业务)
        biz_info = CmdbHandler().biz_id_name({"action": IamActionType.task_history_view})
        biz_permission = list(biz_info.keys())

        # 用户搜索的业务
        search_biz = []
        if params.get("bk_biz_id"):
            # 如果有带筛选条件，则只返回筛选且有权业务的主机
            search_biz = [bk_biz_id for bk_biz_id in params["bk_biz_id"] if bk_biz_id in biz_info]

        # 筛选
        job_result = Job.objects.filter(**filter_values(kwargs))

        if params.get("sort"):
            sort_head = params["sort"]["head"]
            job_result = job_result.extra(select={sort_head: f"JSON_EXTRACT(statistics, '$.{sort_head}')"})
            if params["sort"]["sort_type"] == const.SortType.DEC:
                job_result = job_result.order_by(str("-") + sort_head)
            else:
                job_result = job_result.order_by(sort_head)

        job_result = job_result.values()

        job_list = []
        for job in job_result:
            if not job["end_time"]:
                job["cost_time"] = f'{(timezone.now() - job["start_time"]).seconds}'
            else:
                job["cost_time"] = f'{(job["end_time"] - job["start_time"]).seconds}'
            job["bk_biz_scope_display"] = [biz_info.get(biz) for biz in job["bk_biz_scope"]]
            job["job_type_display"] = const.JOB_TYPE_DICT.get(job["job_type"])

            # 如果任务没有业务则不显示
            if not job["bk_biz_scope"]:
                continue

            # 判断权限
            if set(job["bk_biz_scope"]) - set(biz_permission) == set():
                if set(search_biz) - set(job["bk_biz_scope"]) == set():
                    job_list.append(job)
                    continue
                elif search_biz == biz_permission:
                    job_list.append(job)
                    continue

            # 创建者是自己
            if job["created_by"] == username and not params.get("bk_biz_id"):
                job_list.append(job)
                continue

        # 分页
        paginator = Paginator(job_list, params["pagesize"])
        ret_list = paginator.page(params["page"]).object_list

        return {"total": len(job_list), "list": ret_list}

    def job(self, params: dict, username: str, is_superuser: bool, ticket: str):
        """
        Job 任务处理器

        :param params: 请求参数的字典
        """

        # 获取Hosts中的cloud_id列表、ap_id列表、内网、外网、登录IP列表、bk_biz_scope列表
        bk_cloud_ids = set()
        ap_ids = set()
        bk_biz_scope = set()
        inner_ips = set()
        outer_ips = set()
        login_ips = set()
        is_manual = set()

        for host in params["hosts"]:
            bk_cloud_ids.add(host["bk_cloud_id"])
            bk_biz_scope.add(host["bk_biz_id"])
            inner_ips.add(host["inner_ip"])
            is_manual.add(host["is_manual"])
            if host.get("ap_id"):
                ap_ids.add(host["ap_id"])
            if host.get("outer_ip"):
                outer_ips.add(host["outer_ip"])
            if host.get("login_ip"):
                login_ips.add(host["login_ip"])

        # 如果混合了【手动安装】，【自动安装】则不允许通过
        # 此处暂不和入job validator.
        if len(is_manual) > 1:
            raise MixedOperationError
        else:
            is_manual = list(is_manual)[0]

        bk_biz_scope = list(bk_biz_scope)

        # 获得用户的业务列表
        # 格式 { bk_biz_id: bk_biz_name , ...}
        if params["node_type"] == const.NodeType.PROXY:
            biz_info = CmdbHandler().biz_id_name({"action": IamActionType.proxy_operate})
        else:
            biz_info = CmdbHandler().biz_id_name({"action": IamActionType.agent_operate})

        # 获得相应云区域 id, name, ap_id
        # 格式 { cloud_id: {'bk_cloud_name': name, 'ap_id': id}, ...}
        cloud_info = CloudHandler().list_cloud_info(bk_cloud_ids)

        # 获得接入点列表
        # 格式 { id: name, ...}
        ap_id_name = APHandler().ap_list(ap_ids)

        # 获得用户输入的ip是否存在于数据库中
        # 格式 { bk_cloud_id+ip: { 'bk_host_id': ..., 'bk_biz_id': ..., 'node_type': ...}}
        inner_ip_info = HostHandler().ip_list(inner_ips)
        outer_ip_info = HostHandler().ip_list(outer_ips)
        login_ip_info = HostHandler().ip_list(login_ips)

        # 获得正在执行的任务状态
        task_info = self.task_status_list()

        # 对数据进行校验
        # 重装则校验IP是否存在，存在才可重装
        ip_filter_list, accept_list, proxy_not_alive = job_validate(
            biz_info,
            params,
            cloud_info,
            ap_id_name,
            inner_ip_info,
            outer_ip_info,
            login_ip_info,
            bk_biz_scope,
            task_info,
            username,
            is_superuser,
            ticket,
        )

        if proxy_not_alive != []:
            raise AliveProxyNotExistsError(
                context="不存在可用代理", data={"job_id": "", "ip_filter": self.ugettext_to_unicode(proxy_not_alive)}
            )

        if not accept_list:
            # 如果都被过滤了
            raise AllIpFiltered(
                context="所有IP均被过滤", data={"job_id": "", "ip_filter": self.ugettext_to_unicode(ip_filter_list)}
            )

        if params["op_type"] in [const.OpType.INSTALL, const.OpType.REPLACE, const.OpType.RELOAD]:
            # 安装、替换Proxy操作
            subscription_nodes = self.subscription_install(
                accept_list, params["node_type"], cloud_info, biz_info, username
            )
            subscription = self.create_subscription(params["job_type"], subscription_nodes)
        else:
            # 重装、卸载等操作
            # 此步骤需要校验密码、秘钥
            subscription_nodes, ip_filter_list = self.update(accept_list, ip_filter_list, is_manual)
            if not subscription_nodes:
                raise AllIpFiltered(
                    context="所有IP均被过滤", data={"job_id": "", "ip_filter": self.ugettext_to_unicode(ip_filter_list)}
                )
            subscription = self.create_subscription(params["job_type"], subscription_nodes)

        # ugettext_lazy需要转为unicode才可进行序列化
        ip_filter_list = self.ugettext_to_unicode(ip_filter_list)

        # 创建Job
        job = Job.objects.create(
            job_type=params["job_type"],
            bk_biz_scope=bk_biz_scope,
            subscription_id=subscription["subscription_id"],
            task_id_list=[subscription["task_id"]],
            statistics={
                "success_count": 0,
                "failed_count": 0,
                "filter_count": len(ip_filter_list),
                "pending_count": len(subscription_nodes),
                "running_count": 0,
                "total_count": len(ip_filter_list) + len(subscription_nodes),
            },
            error_hosts=ip_filter_list,
            created_by=username,
        )

        # 返回被过滤的ip列表
        return {"job_id": job.id, "ip_filter": ip_filter_list}

    def subscription_install(self, accept_list: list, node_type: str, cloud_info: dict, biz_info: dict, username: str):
        """
        Job 订阅安装任务
        :param accept_list: 所有通过校验需要新安装的主机
        :param node_type: 节点类型
        :param cloud_info: 云区域信息
        :param biz_info: 业务ID及其对应的名称
        :param username: 用户名
        :return
        """

        # 节点变量，用于后续订阅任务注册主机，安装等操作
        subscription_nodes = []
        for host in accept_list:
            inner_ip = host["inner_ip"]
            outer_ip = host.get("outer_ip", "")
            login_ip = host.get("login_ip", "")

            host_ap_id, host_node_type = self.check_ap_and_biz_scope(node_type, host, cloud_info)

            instance_info = {
                "is_manual": host["is_manual"],
                "ap_id": host_ap_id,
                "bk_os_type": const.BK_OS_TYPE[host["os_type"]],
                "bk_host_innerip": inner_ip,
                "bk_host_outerip": outer_ip,
                "login_ip": login_ip,
                "username": username,
                "bk_biz_id": host["bk_biz_id"],
                "bk_biz_name": biz_info.get(host["bk_biz_id"]),
                "bk_cloud_id": host["bk_cloud_id"],
                "bk_cloud_name": cloud_info.get(host["bk_cloud_id"], {}).get("bk_cloud_name"),
                "bk_supplier_account": settings.DEFAULT_SUPPLIER_ACCOUNT,
                "host_node_type": host_node_type,
                "os_type": host["os_type"],
                "auth_type": host.get("auth_type", "MANUAL"),
                "account": host.get("account", "MANUAL"),
                "port": host.get("port"),
                "password": base64.b64encode(host.get("password", "").encode()).decode(),
                "key": base64.b64encode(host.get("key", "").encode()).decode(),
                "retention": host.get("retention", 1),
                "peer_exchange_switch_for_agent": host.get("peer_exchange_switch_for_agent"),
                "bt_speed_limit": host.get("bt_speed_limit"),
            }

            if host.get("bk_host_id"):
                instance_info.update({"bk_host_id": host.get("bk_host_id")})

            # 写入ticket
            if host.get("auth_type") == const.AuthType.TJJ_PASSWORD:
                instance_info["extra_data"] = {"oa_ticket": host["ticket"]}

            # 写入节点变量
            subscription_nodes.append(
                {
                    "bk_supplier_account": settings.DEFAULT_SUPPLIER_ACCOUNT,
                    "bk_cloud_id": host["bk_cloud_id"],
                    "ip": inner_ip,
                    "instance_info": instance_info,
                }
            )

        return subscription_nodes

    def update(self, accept_list: list, ip_filter_list: list, is_manual: bool = False):
        """
        用于更新identity认证信息
        :param accept_list: 所有需要修改的数据
        :param ip_filter_list: 过滤数据
        """

        identity_to_create = []
        host_to_create = []

        identity_id_to_delete = []
        host_id_to_delete = []

        # 获得需要修改的认证信息的rentention
        if not is_manual:
            # 非手动模式需要认证信息
            identity_info = {
                identity["bk_host_id"]: {
                    "auth_type": identity["auth_type"],
                    "retention": identity["retention"],
                    "account": identity["account"],
                    "password": identity["password"],
                    "key": identity["key"],
                    "port": identity["port"],
                    "extra_data": identity["extra_data"],
                }
                for identity in IdentityData.objects.filter(
                    bk_host_id__in=[host["bk_host_id"] for host in accept_list]
                ).values("bk_host_id", "auth_type", "retention", "account", "password", "key", "port", "extra_data")
            }
        else:
            # 手动模式无需认证信息
            identity_info = {}

        host_info = {
            host["bk_host_id"]: {
                "bk_host_id": host["bk_host_id"],
                "bk_biz_id": host["bk_biz_id"],
                "bk_cloud_id": host["bk_cloud_id"],
                "inner_ip": host["inner_ip"],
                "outer_ip": host["outer_ip"],
                "login_ip": host["login_ip"],
                "data_ip": host["data_ip"],
                "os_type": host["os_type"],
                "node_type": host["node_type"],
                "ap_id": host["ap_id"],
                "upstream_nodes": host["upstream_nodes"],
                "created_at": host["created_at"],
                "updated_at": host["updated_at"],
                "is_manual": host["is_manual"],
                "extra_data": host["extra_data"],
            }
            for host in Host.objects.filter(bk_host_id__in=[host["bk_host_id"] for host in accept_list]).values()
        }

        # 认证信息和Host校验
        update_data_info, ip_filter_list = bulk_update_validate(
            host_info, accept_list, identity_info, ip_filter_list, is_manual
        )

        # 准备对需要修改的identity数据bulk_create
        for host in update_data_info["modified_identity"]:
            update_time = timezone.now()
            the_identity = identity_info[host["bk_host_id"]]
            # 更新ticket
            if host.get("auth_type") == const.AuthType.TJJ_PASSWORD:
                extra_data = {"oa_ticket": host.get("ticket")}
            else:
                extra_data = the_identity["extra_data"]
            identity_to_create.append(
                IdentityData(
                    **{
                        "bk_host_id": host["bk_host_id"],
                        "auth_type": host.get("auth_type", the_identity["auth_type"]),
                        "account": host.get("account", the_identity["account"]),
                        "password": host.get("password", the_identity["password"]),
                        "port": host.get("port", the_identity["port"]),
                        "key": host.get("key", the_identity["key"]),
                        "retention": host.get("retention", the_identity["retention"]),
                        "extra_data": extra_data,
                        "updated_at": update_time,
                    }
                )
            )
            identity_id_to_delete.append(host["bk_host_id"])

        # 准备对需要修改的Host数据bulk_create
        for host in update_data_info["modified_host"]:
            # 如果 操作系统 或 接入点 发生修改
            update_time = timezone.now()
            origin_host = host_info[host["bk_host_id"]]
            host_to_create.append(
                Host(
                    **{
                        "bk_host_id": origin_host["bk_host_id"],
                        "bk_biz_id": origin_host["bk_biz_id"],
                        "bk_cloud_id": origin_host["bk_cloud_id"],
                        "inner_ip": origin_host["inner_ip"],
                        "outer_ip": origin_host["outer_ip"],
                        "login_ip": host.get("login_ip", origin_host["login_ip"]),
                        "data_ip": origin_host["data_ip"],
                        "os_type": host.get("os_type", origin_host["os_type"]),
                        "node_type": origin_host["node_type"],
                        "ap_id": host.get("ap_id", origin_host["ap_id"]),
                        "upstream_nodes": origin_host["upstream_nodes"],
                        "created_at": origin_host["created_at"],
                        "updated_at": update_time,
                        "is_manual": origin_host["is_manual"],
                        "extra_data": {
                            "peer_exchange_switch_for_agent": host.get(
                                "peer_exchange_switch_for_agent",
                                origin_host["extra_data"].get("peer_exchange_switch_for_agent"),
                            ),
                            "bt_speed_limit": host.get(
                                "bt_speed_limit", origin_host["extra_data"].get("bt_speed_limit")
                            ),
                        },
                    }
                )
            )
            host_id_to_delete.append(host["bk_host_id"])

        with transaction.atomic():
            # 删除需要修改的原数据
            IdentityData.objects.filter(bk_host_id__in=identity_id_to_delete).delete()
            Host.objects.filter(bk_host_id__in=host_id_to_delete).delete()
            # bulk_create创建新的信息
            IdentityData.objects.bulk_create(identity_to_create)
            Host.objects.bulk_create(host_to_create)

        return update_data_info["subscription_host_ids"], ip_filter_list

    def operate(self, params: dict, username: str, is_superuser: bool):
        """
        用于只有bk_host_id参数的下线、重启等操作
        :param params: 任务类型及host_id
        :param is_superuser: 是否超管
        """

        # 获得正在执行的任务状态
        task_info = self.task_status_list()

        if params["node_type"] == const.NodeType.PROXY:
            # 是否为针对代理的操作，用户有权限获取的业务
            # 格式 { bk_biz_id: bk_biz_name , ...}
            user_biz = CmdbHandler().biz_id_name({"action": IamActionType.proxy_operate})
            filter_node_types = [const.NodeType.PROXY]
            is_proxy = True
        else:
            # 用户有权限获取的业务
            # 格式 { bk_biz_id: bk_biz_name , ...}
            user_biz = CmdbHandler().biz_id_name({"action": IamActionType.agent_operate})
            filter_node_types = [const.NodeType.AGENT, const.NodeType.PAGENT]
            is_proxy = False

        if params.get("exclude_hosts") is not None:
            # 跨页全选
            db_host_sql = (
                HostHandler()
                .multiple_cond_sql(params, user_biz, proxy=is_proxy)
                .exclude(bk_host_id__in=params.get("exclude_hosts", []))
                .values("bk_host_id", "bk_biz_id", "bk_cloud_id", "inner_ip", "node_type", "os_type")
            )

        else:
            # 不是跨页全选
            db_host_sql = Host.objects.filter(
                bk_host_id__in=params["bk_host_id"], node_type__in=filter_node_types
            ).values("bk_host_id", "bk_biz_id", "bk_cloud_id", "inner_ip", "node_type", "os_type")

        # 校验器进行校验
        db_host_ids, host_biz_scope = operate_validator(list(db_host_sql), user_biz, username, task_info, is_superuser)
        subscription = self.create_subscription(params["job_type"], db_host_ids)

        # 创建Job
        job = Job.objects.create(
            job_type=params["job_type"],
            subscription_id=subscription["subscription_id"],
            task_id_list=[subscription["task_id"]],
            statistics={
                "success_count": 0,
                "failed_count": 0,
                "filter_count": 0,
                "pending_count": len(db_host_ids),
                "running_count": 0,
                "total_count": len(db_host_ids),
            },
            error_hosts=[],
            created_by=username,
            bk_biz_scope=list(set(host_biz_scope)),
        )

        return {"job_id": job.id}

    def create_subscription(self, job_type, nodes: list):
        """
        创建订阅任务
        :param job_type: INSTALL_AGENT
        :param nodes: 任务范围

        1.重装、卸载等操作
        [{"bk_host_id": 1}, {"bk_host_id": 2}]

        2.新装，替换：
        [
            {
                "bk_supplier_account": "0",
                "bk_cloud_id": 0,
                "ip": "127.0.0.1",
                "instance_info": {
                    "ap_id": 1,
                    "bk_os_type": "1",
                    "bk_host_innerip": "127.0.0.1",
                    "bk_host_outerip": "127.0.0.1",
                    "bk_biz_id": 2,
                    "bk_biz_name": "蓝鲸",
                    "bk_cloud_id": 0,
                    "bk_cloud_name": "default area",
                    "bk_supplier_account": "0",
                    "auth_type": "PASSWORD",
                    "account": "root",
                    "port": 22,
                    "auth_type": "PASSWORD",
                    "password": "xxx",
                    "key": "",
                    "retention": 1
                }
            }
        ]
        :return:
        """
        params = {
            "run_immediately": True,
            "bk_app_code": "nodeman",
            "bk_username": "admin",
            "scope": {"node_type": "INSTANCE", "object_type": "HOST", "nodes": nodes},
            "steps": [
                {
                    "id": "agent",
                    "type": "AGENT",
                    "config": {"job_type": job_type},
                    "params": {"context": {}, "blueking_language": get_language()},
                }
            ],
        }
        return NodeApi.create_subscription(params)

    def retry(self, instance_id_list: list, username: str):
        """
        重试部分实例或主机
        :param username: 用户名
        :param instance_id_list: 需重试的实例列表
        :return: task_id_list
        """

        # 检测是否有权限
        self.check_job_permission(username, self.data.bk_biz_scope)

        params = {
            "subscription_id": self.data.subscription_id,
            "instance_id_list": instance_id_list,
        }
        task_id = NodeApi.retry_subscription_task(params)["task_id"]
        self.data.task_id_list.append(task_id)
        if instance_id_list:
            running_count = self.data.statistics["running_count"] + len(instance_id_list)
            failed_count = self.data.statistics["failed_count"] - len(instance_id_list)
        else:
            running_count = self.data.statistics["failed_count"]
            failed_count = 0
        self.data.statistics.update({"running_count": running_count, "failed_count": failed_count})
        self.data.status = const.JobStatusType.RUNNING
        self.data.save()
        return self.data.task_id_list

    def revoke(self, instance_id_list: list, username: str):

        # 检测是否有权限
        self.check_job_permission(username, self.data.bk_biz_scope)

        params = {
            "subscription_id": self.data.subscription_id,
        }
        if instance_id_list:
            params["instance_id_list"] = instance_id_list
        NodeApi.revoke_subscription_task(params)
        self.data.status = const.JobStatusType.TERMINATED
        self.data.end_time = timezone.now()
        self.data.save()
        return self.data.task_id_list

    def _get_current_step_display(self, result):
        """
        用于判断当前状态
        :param result: pipeline 返回结果
        :return: node_id: 当前步骤ID 7为已完成, display: 当前步骤中文名
        """
        try:
            sub_steps = result["steps"][0]["target_hosts"][0]["sub_steps"]
        except (IndexError, KeyError):
            return {"node_id": -1, "display": _("节点异常")}
        for step in sub_steps:
            if step["status"] == "RUNNING":
                return {
                    "node_id": step.get("index"),
                    "display": _("正在 {node_name}").format(node_name=step["node_name"]),
                }
            elif step["status"] == "FAILED":
                return {
                    "node_id": step.get("index"),
                    "display": _("{node_name} 失败").format(node_name=step["node_name"]),
                }

        last_step = sub_steps[-1]
        if last_step["status"] == "SUCCESS":
            return {"node_id": 7, "display": _("执行成功")}
        else:
            return {"node_id": -1, "display": _("等待执行")}

    def retrieve(self, params: dict, username: str):
        """
        任务详情页接口
        :param params: 参数
        :param username: 用户名
        """

        # 检测是否有权限
        self.check_job_permission(username, self.data.bk_biz_scope)

        filter_hosts = [
            {
                "bk_host_id": "",
                "inner_ip": host["ip"],
                "bk_cloud_id": "",
                "bk_cloud_name": host.get("bk_cloud_name"),
                "bk_biz_id": "",
                "bk_biz_name": host.get("bk_biz_name"),
                "job_id": host.get("job_id"),
                "status": host.get("status") or "FILTERED",
                "status_display": host.get("msg"),
            }
            for host in self.data.error_hosts
        ]
        task_result = NodeApi.get_subscription_task_status(
            {"subscription_id": self.data.subscription_id, "task_id_list": self.data.task_id_list}
        )

        # 查询后重新统计，避免 pipeline signal 错误的情况
        success_count = 0
        failed_count = 0
        running_count = 0
        pending_count = 0

        task_data = []
        bk_host_ids = []
        for result in task_result:
            host_info = result["instance_info"]["host"]
            status = result["status"]
            bk_host_ids.append(host_info.get("bk_host_id"))
            task_data.append(
                {
                    "instance_id": result["instance_id"],
                    "inner_ip": host_info["bk_host_innerip"],
                    "bk_host_id": host_info.get("bk_host_id"),
                    "bk_cloud_id": host_info["bk_cloud_id"],
                    "bk_cloud_name": host_info.get("bk_cloud_name"),
                    "bk_biz_id": host_info["bk_biz_id"],
                    "bk_biz_name": host_info["bk_biz_name"],
                    "status": result["status"],
                    "node_id": self._get_current_step_display(result).get("node_id"),
                    "status_display": self._get_current_step_display(result).get("display"),
                }
            )
            if status == const.JobStatusType.SUCCESS:
                success_count += 1
            elif status == const.JobStatusType.FAILED:
                failed_count += 1
            elif status == const.JobStatusType.RUNNING:
                running_count += 1
            else:
                pending_count += 1

        host_is_manual = {
            host["bk_host_id"]: {"ap_id": host["ap_id"], "is_manual": host["is_manual"]}
            for host in Host.objects.filter(bk_host_id__in=bk_host_ids).values("bk_host_id", "ap_id", "is_manual")
        }
        for host in task_data:
            host["is_manual"] = host_is_manual.get(host.get("bk_host_id"), {}).get("is_manual", False)
            host["ap_id"] = host_is_manual.get(host.get("bk_host_id"), {}).get("ap_id")
        task_data.extend(filter_hosts)

        if running_count + pending_count == 0:
            # 所有IP都被执行完毕
            if failed_count == 0:
                self.data.status = const.JobStatusType.SUCCESS
            elif success_count == 0:
                self.data.status = const.JobStatusType.FAILED
            else:
                self.data.status = const.JobStatusType.PART_FAILED
            if not self.data.end_time:
                self.data.end_time = timezone.now()

        self.data.statistics.update(
            {
                "success_count": success_count,
                "failed_count": failed_count,
                "running_count": running_count,
                "pending_count": pending_count,
            }
        )
        self.data.save(update_fields=["statistics", "status", "end_time"])

        # 针对搜索条件进行分页和返回数据
        page = params["page"]
        pagesize = params["pagesize"]
        conditions = params.get("conditions")

        # 有搜索条件
        if conditions is not None:
            for condition in conditions:
                # 过滤ip
                if condition["key"] == "ip":
                    ip = condition["value"]
                    task_data = [host for index, host in enumerate(task_data) if host["inner_ip"].find(ip) != -1]

                # 过滤状态字段
                elif condition["key"] == "status":
                    status = condition["value"]
                    task_data = [host for host in task_data if host["status"] in status]

        # 是否需要分页
        if pagesize == -1:
            ret_list = task_data
        else:
            paginator = Paginator(task_data, pagesize)
            ret_list = paginator.page(page).object_list

        return {
            "job_type": self.data.job_type,
            "job_type_display": const.JOB_TYPE_DICT.get(self.data.job_type, ""),
            "ip_filter_list": [host["ip"] for host in self.data.error_hosts],
            "total": len(task_data),
            "list": ret_list,
            "statistics": self.data.statistics,
            "status": self.data.status,
            "start_time": self.data.start_time,
        }

    @staticmethod
    def get_log_base(subscription_id: int, instance_id: int) -> list:
        """
        根据订阅任务ID，实例ID，获取日志
        :param subscription_id: 订阅任务ID
        :param instance_id: 实例ID
        :return: 日志列表
        """
        params = {"subscription_id": subscription_id, "instance_id": instance_id}
        task_result_detail = NodeApi.get_subscription_task_detail(params)
        logs = []
        if task_result_detail.get("steps"):
            if task_result_detail["steps"][0].get("target_hosts"):
                for step in task_result_detail["steps"][0]["target_hosts"][0].get("sub_steps"):
                    logs.append(
                        {
                            "step": step["node_name"],
                            "status": step["status"],
                            "log": step["log"],
                            "start_time": step.get("start_time"),
                            "finish_time": step.get("finish_time"),
                        }
                    )
        return logs

    def get_log(self, instance_id: int, username: str) -> list:
        """
        获得日志
        :param instance_id: 实例ID
        :param username: 用户名
        :return: 日志列表
        """

        # 检测是否有权限
        self.check_job_permission(username, self.data.bk_biz_scope)

        # 获得并返回日志
        return JobHandler.get_log_base(self.data.subscription_id, instance_id)

    def collect_log(self, instance_id: int, username: str) -> list:
        self.check_job_permission(username, self.data.bk_biz_scope)

        res = NodeApi.collect_subscription_task_detail({"job_id": self.job_id, "instance_id": instance_id})
        return res

    def retry_node(self, instance_id: str, username: str):
        """
        安装过程原子粒度重试
        :param instance_id: 实例id，eg： host|instance|host|20.7.18.2-0-0
        :param username: 用户名
        :return: 重试pipeline节点id，重试节点名称
        {
            "retry_node_id": "6f48169ed1193574961757a57d03a778",
            "retry_node_name": "安装"
        }
        """

        # 检查是否有权限
        self.check_job_permission(username, self.data.bk_biz_scope)

        params = {
            "subscription_id": self.data.subscription_id,
            "instance_id": instance_id,
        }
        retry_node_info = NodeApi.retry_node(params)

        # 更新作业执行情况
        running_count = self.data.statistics["running_count"] + 1
        failed_count = self.data.statistics["failed_count"] - 1
        self.data.statistics.update({"running_count": running_count, "failed_count": failed_count})
        self.data.status = const.JobStatusType.RUNNING
        self.data.save(update_fields=["statistics", "status"])

        return retry_node_info
