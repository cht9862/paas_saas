import random
from unittest.mock import patch

from django.test import TestCase

from apps.node_man import constants as const
from apps.node_man.handlers.meta import MetaHandler
from apps.node_man.models import GlobalSettings, Host, ProcessStatus, Cloud, Job
from apps.node_man.tests.utils import (
    MockClient,
    create_job,
    create_cloud_area,
    create_host,
    SEARCH_BUSINESS,
    cmdb_or_cache_biz,
)


class TestMeta(TestCase):
    def fetch_host_unique_col_count(self, col):
        """
        返回Host中指定列的唯一值
        :param col: 列名
        :return: 唯一值得数量
        """
        host_condition = (
            Host.objects.filter(node_type__in=[const.NodeType.AGENT, const.NodeType.PAGENT])
            .extra(
                select={
                    "status": f"{ProcessStatus._meta.db_table}.status",
                    "version": f"{ProcessStatus._meta.db_table}.version",
                },
                tables=[ProcessStatus._meta.db_table],
            )
            .values_list(col, flat=True)
            .distinct()
        )
        return set(host_condition)

    def fetch_cloud_unique_col_count(self, col):
        """
        返回Cloud中指定列的唯一值
        :param col: 列名
        :return: 唯一值得数量
        """
        return Cloud.objects.values_list(col, flat=True).distinct().count()

    def fetch_Job_unique_col_count(self):
        """
        返回Job中指定列的唯一值
        :return: 唯一值的数量
        """
        # 获得4列的所有值
        job_condition = list(Job.objects.values("created_by", "job_type", "status", "bk_biz_scope").distinct())

        # 初始化各个条件集合
        created_bys = set()
        job_types = set()
        statuses = set()

        for job in job_condition:
            # 判断权限
            if set(job["bk_biz_scope"]) - {biz["bk_biz_id"] for biz in SEARCH_BUSINESS} == set():
                created_bys.add(job["created_by"])
                job_types.add(job["job_type"])
                statuses.add(job["status"])

        return created_bys, job_types, statuses

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_search(self):
        # 服务商搜索接口
        isp_list = [
            {"isp": "Amazon", "isp_icon": "", "isp_name": "AWS"},
            {"isp": "MicroSoft", "isp_icon": "", "isp_name": "Azure"},
            {"isp": "Google", "isp_icon": "", "isp_name": "GCP"},
            {"isp": "SalesForce", "isp_icon": "", "isp_name": "SalesForce"},
            {"isp": "Oracle", "isp_icon": "", "isp_name": "Oracle Cloud"},
            {"isp": "IBM", "isp_icon": "", "isp_name": "IBM Cloud"},
            {"isp": "Aliyun", "isp_icon": "", "isp_name": "阿里云"},
            {"isp": "Tencent", "isp_icon": "", "isp_name": "腾讯云"},
            {"isp": "ECloud", "isp_icon": "", "isp_name": "中国电信"},
            {"isp": "UCloud", "isp_icon": "", "isp_name": "UCloud"},
            {"isp": "MOS", "isp_icon": "", "isp_name": "美团云"},
            {"isp": "KSCLOUD", "isp_icon": "", "isp_name": "金山云"},
            {"isp": "baidu", "isp_icon": "", "isp_name": "百度云"},
            {"isp": "capitalonline", "isp_icon": "", "isp_name": "首都云"},
        ]
        gs = GlobalSettings(key="isp", v_json=isp_list)
        gs.save()
        settings = MetaHandler().search("isp")
        self.assertListEqual(settings["isp"], isp_list)

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_filter_condition(self):
        # Host表头接口
        number = 100
        create_cloud_area(number)
        create_job(number)
        create_host(number, node_type="AGENT")
        # 测试
        result = MetaHandler().filter_condition("host")
        os_types = {res["id"] for res in result[0]["children"]}
        statuses = {res["id"] for res in result[1]["children"]}
        versions = {res["id"] for res in result[3]["children"]}

        self.assertEqual(os_types, self.fetch_host_unique_col_count("os_type"))
        self.assertEqual(statuses, self.fetch_host_unique_col_count("status"))
        self.assertEqual(versions, self.fetch_host_unique_col_count("version"))

        category = "job"
        result = MetaHandler().filter_condition(category)
        api_created_bys = {res["id"] for res in result[1]["children"]}
        api_job_types = {res["id"] for res in result[2]["children"]}
        api_statuses = {res["id"] for res in result[3]["children"]}
        created_bys, job_types, statuses = self.fetch_Job_unique_col_count()
        self.assertEqual(result[0], {"name": "任务ID", "id": "job_id"})
        self.assertEqual(api_created_bys, created_bys)
        self.assertEqual(api_job_types, job_types)
        self.assertEqual(api_statuses, statuses)

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_fetch_plugin_list_condition(self):
        # 插件表头接口
        number = 100
        create_cloud_area(number)
        create_job(number)
        host_to_create, _, _ = create_host(number)
        process_to_create = []
        for host in host_to_create:
            process_to_create.append(
                ProcessStatus(
                    bk_host_id=host.bk_host_id,
                    proc_type=const.ProcType.PLUGIN,
                    version=f"{random.randint(1, 10)}",
                    name=const.HEAD_PLUGINS[random.randint(0, len(const.HEAD_PLUGINS) - 1)],
                    status="RUNNING",
                )
            )
        # 测试
        MetaHandler().filter_condition("plugin")

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    @patch("apps.node_man.handlers.cmdb.get_request_username", return_value="special_test")
    def test_fetch_plugin_list_condition_no_permission(self, *args, **kwargs):
        self.maxDiff = None
        # 插件表头接口
        number = 100
        create_cloud_area(number)
        create_job(number)
        host_to_create, _, _ = create_host(number)
        process_to_create = []
        for host in host_to_create:
            process_to_create.append(
                ProcessStatus(
                    bk_host_id=host.bk_host_id,
                    proc_type=const.ProcType.PLUGIN,
                    version=f"{random.randint(1, 10)}",
                    name=const.HEAD_PLUGINS[random.randint(0, len(const.HEAD_PLUGINS) - 1)],
                    status="RUNNING",
                )
            )
        expected_result = [{"name": "IP", "id": "inner_ip"}]
        plugin_names = const.HEAD_PLUGINS
        for plugin_name in plugin_names:
            expected_result.extend(
                [
                    {
                        "id": plugin_name,
                        "name": plugin_name,
                        # 没有任何业务权限拿不到相应数据
                        "children": [{"id": -1, "name": "无版本"}],
                    },
                    {
                        "id": "{}_status".format(plugin_name),
                        "name": "{}状态".format(plugin_name),
                        "children": [
                            {"name": "正常", "id": const.ProcStateType.RUNNING},
                            {"name": "异常", "id": const.ProcStateType.TERMINATED},
                            {"name": "未注册", "id": const.ProcStateType.UNREGISTER},
                        ],
                    },
                ]
            )
        result = MetaHandler().filter_condition("plugin")
        self.assertEqual(result, expected_result)

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_job_setting(self):
        # 相关参数保存接口
        MetaHandler().job_setting({"test": 123})
