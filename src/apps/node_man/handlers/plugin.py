# -*- coding: utf-8 -*-
from collections import defaultdict

from apps.utils import APIModel
from apps.node_man import constants as const, constants
from apps.node_man.constants import IamActionType
from apps.node_man.models import Cloud, ProcessStatus, JobTask, Packages, Host, Job
from apps.node_man.handlers.cmdb import CmdbHandler
from apps.node_man.handlers.validator import operate_validator
from apps.node_man.handlers.host import HostHandler
from common.api import NodeApi


class PluginHandler(APIModel):
    """
    插件处理器
    """

    @staticmethod
    def list(params: dict):
        """
        查询主机
        :param params: 经校验后的数据
        """

        # 用户有权限获取的业务
        # 格式 { bk_biz_id: bk_biz_name , ...}
        user_biz = CmdbHandler().biz_id_name({"action": IamActionType.plugin_view})

        # 用户主机操作权限
        plugin_operate_bizs = CmdbHandler().biz_id_name({"action": IamActionType.plugin_operate})

        # 页面
        if params["pagesize"] != -1:
            # 如果是正常数量
            begin = (params["page"] - 1) * params["pagesize"]
            end = (params["page"]) * params["pagesize"]
        else:
            # 全部
            begin = None
            end = None
            # 跨页全选模式，仅返回用户有权限操作的主机
            user_biz = plugin_operate_bizs

        # 查询
        hosts_status_sql = (
            HostHandler()
            .multiple_cond_sql(params, user_biz, plugin=True)
            .exclude(bk_host_id__in=params.get("exclude_hosts", []))
        )

        # 计算总数
        hosts_status_count = hosts_status_sql.count()

        if params["only_ip"] is False:
            # sql分页查询获得数据
            hosts_status = list(
                hosts_status_sql[begin:end].values(
                    "bk_cloud_id",
                    "bk_biz_id",
                    "bk_host_id",
                    "node_type",
                    "os_type",
                    "inner_ip",
                    "status",
                    "version",
                    "node_from",
                )
            )
        else:
            # 如果仅需要IP数据
            hosts_status = [host["inner_ip"] for host in list(hosts_status_sql[begin:end].values("inner_ip"))]
            result = {"total": hosts_status_count, "list": hosts_status}
            return result

        # 分页结果的Host_id, cloud_id集合
        bk_host_ids = [hs["bk_host_id"] for hs in hosts_status]
        bk_cloud_ids = [hs["bk_cloud_id"] for hs in hosts_status]

        # 获得云区域名称
        cloud_name = dict(
            Cloud.objects.filter(bk_cloud_id__in=bk_cloud_ids).values_list("bk_cloud_id", "bk_cloud_name")
        )
        cloud_name[0] = "直连区域"

        # 获得 Job Result 数据
        job_status = JobTask.objects.filter(bk_host_id__in=bk_host_ids).values(
            "bk_host_id", "instance_id", "job_id", "status", "current_step"
        )
        host_id_job_status = {
            status["bk_host_id"]: {
                "instance_id": status["instance_id"],
                "job_id": status["job_id"],
                "status": status["status"],
                "current_step": status["current_step"],
            }
            for status in job_status
        }

        # 获得每个Host下的插件
        host_plugin = defaultdict(list)
        agent_status = dict()
        plugins = ProcessStatus.objects.filter(bk_host_id__in=bk_host_ids, source_type="default").values()
        for plugin in plugins:
            host_plugin[plugin["bk_host_id"]].append(
                {
                    "name": plugin["name"],
                    "status": plugin["status"],
                    "version": plugin["version"],
                    "host_id": plugin["bk_host_id"],
                }
            )
            if plugin["name"] == ProcessStatus.GSE_AGENT_PROCESS_NAME:
                agent_status[plugin["bk_host_id"]] = {"status": plugin["status"], "version": plugin["version"]}

        # 汇总
        for hs in hosts_status:
            bk_host_id = hs["bk_host_id"]
            hs.update(agent_status.get(bk_host_id, {}))
            hs["status_display"] = const.PROC_STATUS_CHN.get(hs["status"], "")
            hs["bk_cloud_name"] = cloud_name.get(hs["bk_cloud_id"])
            hs["bk_biz_name"] = user_biz.get(hs["bk_biz_id"], "")
            hs["job_result"] = host_id_job_status.get(bk_host_id, {})
            hs["plugin_status"] = host_plugin.get(bk_host_id, [])
            hs["operate_permission"] = hs["bk_biz_id"] in plugin_operate_bizs

        result = {"total": hosts_status_count, "list": hosts_status}

        return result

    @staticmethod
    def operate(params: dict, username: str, is_superuser: bool):
        """
        用于只有bk_host_id参数的插件操作
        :param params: 任务类型及host_id
        :param username: 用户名
        :param is_superuser: 是否为超级用户
        """

        # 用户有权限获取的业务
        # 格式 { bk_biz_id: bk_biz_name , ...}
        user_biz = CmdbHandler().biz_id_name({"action": IamActionType.plugin_operate})

        if params.get("exclude_hosts") is not None:
            # 跨页全选
            db_host_sql = (
                HostHandler()
                .multiple_cond_sql(params, user_biz, plugin=True)
                .exclude(bk_host_id__in=params.get("exclude_hosts", []))
                .values("bk_host_id", "bk_biz_id", "bk_cloud_id", "inner_ip", "node_type", "os_type")
            )

        else:
            # 不是跨页全选
            db_host_sql = Host.objects.filter(
                bk_host_id__in=params["bk_host_id"],
                node_type__in=[const.NodeType.AGENT, const.NodeType.PAGENT, const.NodeType.PROXY],
            ).values("bk_host_id", "bk_biz_id", "bk_cloud_id", "inner_ip", "node_type", "os_type")

        # 校验器进行校验
        db_host_ids, host_biz_scope = operate_validator(list(db_host_sql), user_biz, username, {}, is_superuser)

        # 插件名称
        plugin_params = params["plugin_params"]
        plugin_name = plugin_params["name"]
        plugin_version = plugin_params["version"]
        subscription = PluginHandler.create_subscription(
            params["job_type"],
            db_host_ids,
            plugin_name,
            plugin_version,
            plugin_params.get("keep_config"),
            plugin_params.get("no_restart"),
        )

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

    @staticmethod
    def create_subscription(
        job_type: str, nodes: list, name: str, version: str, keep_config: bool = None, no_restart: bool = None
    ):
        """

        创建插件订阅任务
        :param job_type: MAIN_JOB_PLUGIN
        :param nodes: 任务范围
        :param name: 插件名
        :param version: 插件版本
        :param keep_config: 保留原有配置
        :param no_restart: 不重启进程
        :return:
        """
        params = {
            "run_immediately": True,
            "bk_app_code": "nodeman",
            "bk_username": "admin",
            "scope": {"node_type": "INSTANCE", "object_type": "HOST", "nodes": nodes},
            "steps": [
                {
                    "config": {
                        "config_templates": [{"name": "{}.conf".format(name), "version": "latest", "is_main": True}],
                        "plugin_name": name,
                        "plugin_version": version,
                        "job_type": job_type,
                    },
                    "type": "PLUGIN",
                    "id": name,
                    "params": {"keep_config": keep_config, "no_restart": no_restart},
                }
            ],
        }

        return NodeApi.create_subscription(params)

    @staticmethod
    def get_packages(project, os_type):
        """
        获取某个插件包列表
        """
        return Packages.objects.filter(
            cpu_arch__in=[constants.CpuType.x86_64, constants.CpuType.powerpc], project=project, os=os_type.lower()
        ).order_by("-id")

    @staticmethod
    def get_process_status(bk_host_ids: list):
        """
        获取主机process状态信息
        """
        return ProcessStatus.objects.filter(bk_host_id__in=bk_host_ids)

    @staticmethod
    def get_statistics():
        """
        统计各个插件的安装情况
        """
        hosts = Host.objects.all().values("bk_biz_id", "bk_host_id")

        host_biz_mappings = {host["bk_host_id"]: host["bk_biz_id"] for host in hosts}

        processes = ProcessStatus.objects.filter(source_type=ProcessStatus.SourceType.DEFAULT).values(
            "bk_host_id", "version", "name", "status"
        )

        process_count = defaultdict(int)

        for process in processes:
            if process["bk_host_id"] not in host_biz_mappings:
                continue
            # key: 业务ID，插件名称，插件版本，状态。按照这四个维度进行聚合
            key = (host_biz_mappings[process["bk_host_id"]], process["name"], process["version"], process["status"])
            process_count[key] += 1

        result = [
            {
                "bk_biz_id": bk_biz_id,
                "plugin_name": plugin_name,
                "version": version,
                "status": status,
                "host_count": host_count,
            }
            for (bk_biz_id, plugin_name, version, status), host_count in process_count.items()
        ]
        return result
