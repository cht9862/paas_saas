# -*- coding: utf-8 -*-
from collections import defaultdict
from copy import deepcopy

import mock
from django.test import TestCase

from apps.backend.subscription.tools import get_instances_by_scope, parse_group_id, parse_host_key
from apps.backend.tests.subscription.utils import SEARCH_HOST, SERVICE_DETAIL, TOPO_TREE

# 全局使用的mock
run_task = mock.patch("apps.backend.subscription.tasks.run_subscription_task").start()


class TestTools(TestCase):
    """
    测试tools.py下的函数
    """

    GROUP_ID = "sub_1_host_1"
    HOST_KEY = "10.1.1.10-0-tencent"
    HOST_ID_KEY = "1024"

    def test_parse_group_id(self):
        res = parse_group_id(self.GROUP_ID)
        assert res["subscription_id"] == "1"
        assert res["object_type"] == "host"
        assert res["id"] == "1"

    def test_parse_host_key(self):
        res = parse_host_key(self.HOST_KEY)
        assert res["ip"] == "10.1.1.10"
        assert res["bk_cloud_id"] == "0"
        assert res["bk_supplier_id"] == "tencent"

        res = parse_host_key(self.HOST_ID_KEY)
        assert res["bk_host_id"] == 1024

    def test_get_host_instance_scope(self):
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = SEARCH_HOST
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        instances = get_instances_by_scope(
            {
                "bk_biz_id": 2,
                "object_type": "HOST",
                "node_type": "INSTANCE",
                "nodes": [
                    {"ip": "10.0.1.9", "bk_cloud_id": 0, "bk_supplier_id": 0},
                    {"ip": "10.0.1.16", "bk_cloud_id": 0, "bk_supplier_id": 0},
                ],
            }
        )

        self.assertEqual(len(list(instances.keys())), 2)
        assert "host|instance|host|3" in instances
        assert "host|instance|host|4" in instances

    def test_get_host_topo_scope(self):
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = SEARCH_HOST
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        instances = get_instances_by_scope(
            {
                "bk_biz_id": 2,
                "object_type": "HOST",
                "node_type": "TOPO",
                "nodes": [
                    {"bk_obj_id": "module", "bk_inst_id": 1},
                    {"bk_obj_id": "set", "bk_inst_id": 2},
                    {"bk_obj_id": "test", "bk_inst_id": 1000},
                ],
            }
        )

        self.assertEqual(len(list(instances.keys())), 4)
        assert "host|instance|host|3" in instances
        assert "host|instance|host|4" in instances

        cmdb_client.cc.search_host.call_count = 3

    def test_get_service_topo_scope(self):
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = SEARCH_HOST
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE
        cmdb_client.cc.get_service_instances_detail.return_value = SERVICE_DETAIL

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        instances = get_instances_by_scope(
            {
                "bk_biz_id": 2,
                "object_type": "SERVICE",
                "node_type": "TOPO",
                "nodes": [{"bk_obj_id": "module", "bk_inst_id": 23}],
            }
        )

        self.assertEqual(len(list(instances.keys())), 2)
        for instance_id in instances:
            instance = instances[instance_id]
            self.assertEqual(instance["service"]["bk_module_id"], 23)
            self.assertSetEqual({"process", "scope", "host", "service"}, set(instance.keys()))

    def test_get_service_instance_scope(self):
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = SEARCH_HOST
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE
        service_data = deepcopy(SERVICE_DETAIL)
        service_data["info"] = [x for x in service_data["info"] if x["id"] == 10]
        cmdb_client.cc.get_service_instances_detail.return_value = service_data

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        instances = get_instances_by_scope(
            {"bk_biz_id": 2, "object_type": "SERVICE", "node_type": "INSTANCE", "nodes": [{"id": 10}]}
        )

        self.assertEqual(len(list(instances.keys())), 1)
        for instance_id in instances:
            instance = instances[instance_id]
            self.assertEqual(instance["service"]["id"], 10)
            self.assertSetEqual({"process", "scope", "host", "service"}, set(instance.keys()))
