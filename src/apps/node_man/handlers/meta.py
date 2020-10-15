# -*- coding: utf-8 -*-
import re

from django.utils.translation import ugettext as _
from django.db import connection

from apps.utils import APIModel
from apps.node_man.constants import IamActionType
from apps.node_man.handlers.cmdb import CmdbHandler
from apps.node_man.handlers.cloud import CloudHandler
from apps.node_man.models import GlobalSettings, Host, ProcessStatus, Job
from apps.node_man import constants as const


class MetaHandler(APIModel):
    """
    Meta处理器
    """

    def filter_empty_children(self, condition_result):
        """
        若没有数据，则过滤掉整个字段
        :condition_result: 条件数据
        :return: 过滤后的返回值
        """
        new_condition_result = []
        for condition in condition_result:
            if "children" not in condition:
                new_condition_result.append(condition)
            elif condition["children"] != []:
                new_condition_result.append(condition)
        return new_condition_result

    def regular_agent_version(self, agent_versions):
        """
        统一规范化Agent版本
        :param agent_versions: Agent版本
        :return: 升序后的版本列表
        """

        sort_map = {}
        # 1.60.58
        standard_format = re.compile("(.*)\\.(.*)\\.(.*)")
        # V0.01R060P42
        special_format = re.compile("V(.*)R(.*)[P|D](.*)?W")
        for version in agent_versions:
            version = version.upper()
            if "V" in version:
                result = special_format.findall(version)
                # 处理V0.01这样的数字
            else:
                result = standard_format.findall(version)

            if result != []:
                try:
                    numbers = result[0]
                    first_number = float(numbers[0])
                    if first_number < 1:
                        # 处理0.01这样的数字
                        first_number = first_number * 100
                    sort_map[version] = int(first_number) * 10000 + int(numbers[1]) * 100 + int(numbers[2])
                except BaseException:
                    # 捕捉特殊字符异常
                    sort_map[version] = const.JOB_MAX_VALUE
            else:
                sort_map[version] = const.JOB_MAX_VALUE

        return [item[0] for item in sorted(sort_map.items(), key=lambda item: item[1])]

    def fetch_host_process_unique_col(
        self,
        biz_permission: list,
        col: str,
        node_types: list,
        name: str = ProcessStatus.GSE_AGENT_PROCESS_NAME,
        proc_type: str = "AGENT",
    ):
        """
        返回Host和process_status中指定列的唯一值
        :param biz_permission: 用户有权限的业务
        :param col: 指定列
        :param node_types: 节点类型
        :param name: process 名
        :return: 列的唯一值，数组
        """

        node_type = "'" + "','".join(node_types) + "'"
        biz_permission = ", ".join(str(biz) for biz in biz_permission)
        if not biz_permission:
            biz_permission = "''"

        if col in ["version", "status"]:
            select_sql = f"SELECT distinct {ProcessStatus._meta.db_table}.{col} AS `{col}`"
        else:
            select_sql = f"SELECT distinct {Host._meta.db_table}.{col} AS `{col}`"
        cursor = connection.cursor()
        cursor.execute(
            f"{select_sql} "
            f"FROM `{Host._meta.db_table}` join `{ProcessStatus._meta.db_table}` "
            f"on `{Host._meta.db_table}`.bk_host_id = `{ProcessStatus._meta.db_table}`.bk_host_id "
            f"WHERE (`{Host._meta.db_table}`.`node_type` IN ({node_type}) "
            f"AND `{Host._meta.db_table}`.`bk_biz_id` IN ({biz_permission}) "
            f"AND `{ProcessStatus._meta.db_table}`.`proc_type` = '{proc_type}' "
            f"AND `{ProcessStatus._meta.db_table}`.`name` = '{name}');"
        )

        return cursor

    def fetch_host_condition(self):
        """
        获取Host接口的条件
        :param username: 用户名
        :return: Host接口所有条件
        """

        # 用户有权限的业务
        biz_id_name = CmdbHandler().biz_id_name({"action": IamActionType.agent_view})
        biz_permission = list(biz_id_name.keys())

        # 获得数据
        bk_cloud_tuple = self.fetch_host_process_unique_col(biz_permission, "bk_cloud_id", ["AGENT", "PAGENT"])
        bk_cloud_ids = [item for sublist in bk_cloud_tuple for item in sublist]

        os_type_tuple = self.fetch_host_process_unique_col(biz_permission, "os_type", ["AGENT", "PAGENT"])
        os_types = [item for sublist in os_type_tuple for item in sublist]

        is_manual_tuple = self.fetch_host_process_unique_col(biz_permission, "is_manual", ["AGENT", "PAGENT"])
        is_manuals = [item for sublist in is_manual_tuple for item in sublist]

        status_tuple = self.fetch_host_process_unique_col(biz_permission, "status", ["AGENT", "PAGENT"])
        statuses = [item for sublist in status_tuple for item in sublist]

        version_tuple = self.fetch_host_process_unique_col(biz_permission, "version", ["AGENT", "PAGENT"])
        versions = self.regular_agent_version([item for sublist in version_tuple for item in sublist])

        os_types_children = [{"name": const.OS_CHN.get(os, os), "id": os} for os in os_types if os != ""]
        statuses_children = [
            {"name": const.PROC_STATUS_CHN.get(status, status), "id": status} for status in statuses if status != ""
        ]
        versions_children = [{"name": version, "id": version} for version in versions if version != ""]
        is_manual_children = [{"name": "手动" if is_manual else "远程", "id": is_manual} for is_manual in is_manuals]
        bk_cloud_names = CloudHandler().list_cloud_info(bk_cloud_ids)
        bk_cloud_ids_children = [
            {"name": bk_cloud_names.get(bk_cloud_id, {}).get("bk_cloud_name", bk_cloud_id), "id": bk_cloud_id}
            for bk_cloud_id in bk_cloud_ids
        ]
        return self.filter_empty_children(
            [
                {"name": "操作系统", "id": "os_type", "children": os_types_children},
                {"name": "Agent状态", "id": "status", "children": statuses_children},
                {"name": "安装方式", "id": "is_manual", "children": is_manual_children},
                {"name": "Agent版本", "id": "version", "children": versions_children},
                {"name": "云区域", "id": "bk_cloud_id", "children": bk_cloud_ids_children},
                {"name": "IP", "id": "inner_ip"},
            ]
        )

    def fetch_job_list_condition(self):
        """
        获取任务历史接口的条件
        :param username: 用户名
        :return: Host接口所有条件
        """

        # 获得业务id与名字的映射关系(用户有权限获取的业务)
        biz_permission = list(CmdbHandler().biz_id_name({"action": IamActionType.task_history_view}))

        # 获得4列的所有值
        Job_condition = list(Job.objects.values("created_by", "job_type", "status", "bk_biz_scope").distinct())

        # 初始化各个条件集合
        created_bys = set()
        job_types = set()
        statuses = set()

        for job in Job_condition:
            # 判断权限
            if set(job["bk_biz_scope"]) - set(biz_permission) == set():
                created_bys.add(job["created_by"])
                job_types.add(job["job_type"])
                statuses.add(job["status"])

        created_bys_children = [
            {"name": created_by, "id": created_by} for created_by in created_bys if created_by != ""
        ]

        job_types_children = [
            {"name": const.JOB_TYPE_DICT.get(job_type, job_type), "id": job_type} for job_type in job_types
        ]

        statuses_children = [
            {"name": dict(const.JobStatusType.get_choices()).get(status, status), "id": status} for status in statuses
        ]

        return self.filter_empty_children(
            [
                {"name": "任务ID", "id": "job_id"},
                {"name": "执行者", "id": "created_by", "children": created_bys_children},
                {"name": "任务类型", "id": "job_type", "children": job_types_children},
                {"name": "执行状态", "id": "status", "children": statuses_children},
            ]
        )

    def fetch_plugin_list_condition(self):
        """
        获取插件接口的条件
        :return: Host接口所有条件
        """

        # 用户有权限的业务
        biz_id_name = CmdbHandler().biz_id_name({"action": IamActionType.plugin_view})
        biz_permission = list(biz_id_name.keys())

        # 初始化各个条件集合
        plugin_names = const.HEAD_PLUGINS
        plugin_result = {}

        # 获得数据
        bk_cloud_tuple = self.fetch_host_process_unique_col(biz_permission, "bk_cloud_id", ["AGENT", "PAGENT"])
        bk_cloud_ids = [bk_cloud[0] for bk_cloud in bk_cloud_tuple]
        bk_cloud_names = CloudHandler().list_cloud_info(bk_cloud_ids)
        plugin_result["bk_cloud_id"] = {
            "name": "云区域",
            "value": [
                {"name": bk_cloud_names.get(bk_cloud_id, {}).get("bk_cloud_name", bk_cloud_id), "id": bk_cloud_id}
                for bk_cloud_id in bk_cloud_ids
            ],
        }

        os_type_tuple = self.fetch_host_process_unique_col(biz_permission, "os_type", ["AGENT", "PAGENT"])
        os_types = [os_type[0] for os_type in os_type_tuple]
        plugin_result["os_type"] = {
            "name": "操作系统",
            "value": [{"name": const.OS_CHN.get(os, os), "id": os} for os in os_types if os != ""],
        }

        agent_version_tuple = self.fetch_host_process_unique_col(biz_permission, "version", ["AGENT", "PAGENT"])
        versions = self.regular_agent_version([version[0] for version in agent_version_tuple])
        plugin_result[ProcessStatus.GSE_AGENT_PROCESS_NAME] = {
            "name": "Agent版本",
            "value": [{"name": version, "id": version} for version in versions if version != ""],
        }

        status_tuple = self.fetch_host_process_unique_col(biz_permission, "status", ["AGENT", "PAGENT"])
        statuses = [statuse[0] for statuse in status_tuple]
        plugin_result["status"] = {
            "name": "Agent状态",
            "value": [
                {"name": const.PROC_STATUS_CHN.get(status, status), "id": status} for status in statuses if status != ""
            ],
        }

        # 各个插件的版本
        for plugin_name in plugin_names:
            plugin_version_tuple = self.fetch_host_process_unique_col(
                biz_permission, "version", ["AGENT", "PAGENT", "PROXY"], name=plugin_name, proc_type="PLUGIN"
            )
            plugin_versions = [plugin_version[0] for plugin_version in plugin_version_tuple]
            plugin_result[plugin_name] = {"name": plugin_name, "value": [{"name": _("无版本"), "id": -1}]}
            plugin_result["{}_status".format(plugin_name)] = {
                "name": _("{}状态").format(plugin_name),
                "value": [
                    {"name": _("正常"), "id": const.ProcStateType.RUNNING},
                    {"name": _("异常"), "id": const.ProcStateType.TERMINATED},
                    {"name": _("未注册"), "id": const.ProcStateType.UNREGISTER},
                ],
            }
            for plugin_version in plugin_versions:
                if plugin_version:
                    plugin_result[plugin_name]["value"].append({"name": plugin_version, "id": plugin_version})

        # 返回值
        ret_value = [{"name": "IP", "id": "inner_ip"}]
        ret_value.extend(
            [
                {
                    "name": plugin_result[name]["name"],
                    "id": name if name != ProcessStatus.GSE_AGENT_PROCESS_NAME else "version",
                    "children": list(plugin_result[name]["value"]),
                }
                for name in plugin_result
            ]
        )

        return self.filter_empty_children(ret_value)

    def filter_condition(self, category):
        """
        获取过滤条件
        :param category: 接口, host, cloud, Job等
        :return: 某接口所有条件
        """

        if category == "host":
            return self.fetch_host_condition()
        elif category == "job":
            return self.fetch_job_list_condition()
        elif category == "plugin":
            return self.fetch_plugin_list_condition()

    def search(self, key):
        """
        查询相关配置
        """

        settings = dict(GlobalSettings.objects.filter(key=key).values_list("key", "v_json"))
        return settings

    def job_setting(self, params):
        """
        查询相关配置
        :param params: 请求参数
        """

        user_setting = {}
        for setting in params:
            user_setting[setting] = params[setting]
        global_setting, state = GlobalSettings.objects.get_or_create(
            key="job_settings", defaults={"v_json": user_setting}
        )

        if not state:
            # 如果已经有相关配置
            user_setting = global_setting.v_json
            for setting in params:
                user_setting[setting] = params[setting]
            global_setting.v_json = user_setting
            global_setting.save()
