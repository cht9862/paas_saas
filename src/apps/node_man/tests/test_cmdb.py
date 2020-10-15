import random
from unittest.mock import patch

from django.test import TestCase

from apps.node_man.exceptions import CloudNotExistError, CloudUpdateAgentError, CmdbAddCloudPermissionError
from apps.node_man.handlers.cmdb import CmdbHandler
from apps.node_man.tests.utils import (
    MockClient,
    MockClientRaise,
    create_host,
    DIGITS,
    SEARCH_BUSINESS,
    cmdb_or_cache_biz,
)


class Test_Cmdb(TestCase):
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_or_cache_biz(self):
        # 未缓存
        result = CmdbHandler().cmdb_or_cache_biz("admin")
        self.assertEqual(result, {"info": SEARCH_BUSINESS})
        # 缓存
        result = CmdbHandler().cmdb_or_cache_biz("admin")
        self.assertEqual(result, {"info": SEARCH_BUSINESS})

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_or_cache_topo(self):
        # 未缓存
        result = CmdbHandler().cmdb_or_cache_topo("admin", user_biz={2: "蓝鲸"}, biz_host_id_map={2: [1]})
        self.assertEqual(result, {1: ["蓝鲸 / test / test_module"]})

        # 缓存
        result = CmdbHandler().cmdb_or_cache_topo("admin", user_biz={2: "蓝鲸"}, biz_host_id_map={2: [1]})
        self.assertEqual(result, {1: ["蓝鲸 / test / test_module"]})

    # 测试cmdb_cache内的异常分支
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClientRaise)
    def test_cmdb_or_cache_biz_raise(self):
        result = CmdbHandler().cmdb_or_cache_biz("admin")
        self.assertEqual(result, {"info": []})

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_biz_id_name(self):
        biz_id_name = CmdbHandler().biz_id_name("admin")
        self.assertListEqual(list(biz_id_name.keys()), [biz["bk_biz_id"] for biz in SEARCH_BUSINESS])

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_update_host(self):
        host_to_create, _, _ = create_host(1, bk_host_id=10, ip="255.255.255.255")
        CmdbHandler().cmdb_update_host(host_to_create[0].bk_host_id, {"bk_host_innerip": "255.255.255.253"})

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_find_host_topo(self):
        CmdbHandler().find_host_topo("admin", bk_biz_id=2, bk_host_ids=[1], topology={}, user_biz={2: "蓝鲸"})

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_update_host_cloud(self):
        host_to_create, _, _ = create_host(1, bk_host_id=10, ip="255.255.255.255")
        update_cloud = {
            "bk_host_ids": host_to_create[0].bk_host_id,
            "bk_cloud_id": 1111,
        }
        CmdbHandler().cmdb_update_host_cloud(update_cloud)

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_add_cloud(self):
        bk_cloud_name = "".join(random.choice(DIGITS) for x in range(8))
        id = CmdbHandler().add_cloud(bk_cloud_name)
        self.assertLessEqual(int(id), 10000)

        # CmdbAddCloudPermissionError
        bk_cloud_name = "abc"
        self.assertRaises(CmdbAddCloudPermissionError, CmdbHandler().add_cloud, bk_cloud_name)

        # create_inst
        bk_cloud_name = "bbc"
        id = CmdbHandler().add_cloud(bk_cloud_name)
        self.assertLessEqual(int(id), 1000)

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_delete_cloud(self):
        bk_cloud_id = 1
        CmdbHandler().delete_cloud(bk_cloud_id)

        bk_cloud_id = 8888
        self.assertRaises(CloudUpdateAgentError, CmdbHandler().delete_cloud, bk_cloud_id)

        bk_cloud_id = 9999
        CmdbHandler().delete_cloud(bk_cloud_id)

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_get_cloud(self):
        # ComponentCallError
        bk_cloud_name = "abc"
        bk_cloud_id = CmdbHandler().get_cloud(bk_cloud_name)
        self.assertLessEqual(bk_cloud_id, 1000)

        # CloudNotExists
        bk_cloud_name = "bcd"
        self.assertRaises(CloudNotExistError, CmdbHandler().get_cloud, bk_cloud_name)

        # normal
        bk_cloud_name = "".join(random.choice(DIGITS) for x in range(8))
        bk_cloud_id = CmdbHandler().get_cloud(bk_cloud_name)
        self.assertLessEqual(bk_cloud_id, 1000)

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_rename_cloud(self):
        # ComponentCallError
        CmdbHandler().rename_cloud(random.randint(0, 1000), "".join(random.choice(DIGITS) for x in range(8)))

        # normal
        CmdbHandler().rename_cloud(random.randint(10000, 100000), "".join(random.choice(DIGITS) for x in range(8)))

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_get_or_create_cloud(self):
        bk_cloud_name = "b&*"
        CmdbHandler().get_or_create_cloud(bk_cloud_name)

        # normal
        bk_cloud_name = "".join(random.choice(DIGITS) for x in range(8))
        id = CmdbHandler().get_or_create_cloud(bk_cloud_name)
        self.assertLessEqual(id, 1000)

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_biz_inst_topo(self):
        result = CmdbHandler().cmdb_biz_inst_topo(biz=1)
        self.assertEqual(result[0]["child"][0]["bk_inst_id"], 10166)

        # 异常
        result = CmdbHandler().cmdb_biz_inst_topo(biz=2)
        self.assertEqual(result, [])

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_biz_free_inst_topo(self):
        result = CmdbHandler().cmdb_biz_free_inst_topo(biz=1)
        self.assertEqual(result["bk_set_id"], 10)

        # 异常
        result = CmdbHandler().cmdb_biz_free_inst_topo(biz=2)
        self.assertEqual(result, {"info": []})

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_cmdb_hosts_by_biz(self):
        result = CmdbHandler().cmdb_hosts_by_biz(start=0, bk_biz_id=1, bk_set_ids=[1], bk_module_ids=[1])
        self.assertEqual(result["info"][0]["bk_host_id"], 14110)

        # 异常
        result = CmdbHandler().cmdb_hosts_by_biz(start=0, bk_biz_id=2, bk_set_ids=[1], bk_module_ids=[1])
        self.assertEqual(result, {"info": []})

    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_fetch_host_ids_by_biz(self):
        result = CmdbHandler().fetch_host_ids_by_biz(bk_biz_id=1, bk_set_ids=[1], bk_module_ids=[1])
        self.assertEqual(result, [14110])

        # 异常
        result = CmdbHandler().fetch_host_ids_by_biz(bk_biz_id=2, bk_set_ids=[1], bk_module_ids=[1])
        self.assertEqual(result, [])

        # 异步
        result = CmdbHandler().fetch_host_ids_by_biz(bk_biz_id=-1, bk_set_ids=[1], bk_module_ids=[1])
        self.assertEqual(len(result), 555)

    @patch("apps.node_man.handlers.cmdb.CmdbHandler.cmdb_or_cache_biz", cmdb_or_cache_biz)
    @patch("apps.node_man.handlers.cmdb.client_v2", MockClient)
    def test_fetch_topo(self):
        params = {"bk_biz_id": 1}
        result = CmdbHandler().fetch_topo(params, "admin", True)
        self.assertEqual(result[1]["id"], 10166)

        # 异常
        params = {"bk_biz_id": 2}
        result = CmdbHandler().fetch_topo(params, "admin", True)
        self.assertEqual(result, [{"children": [], "id": None, "name": None, "type": "set"}])
