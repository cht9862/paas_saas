# -*- coding: utf-8 -*-
from collections import defaultdict

import mock
import ujson as json
from django.test import Client, TestCase

from apps.backend.plugin.manager import PluginManager
from apps.backend.tests.subscription.utils import SEARCH_HOST, TOPO_TREE, DEFAULT_AP_ID
from apps.node_man.models import (
    GsePluginDesc,
    Host,
    Packages,
    PluginConfigTemplate,
    ProcControl,
    ProcessStatus,
    Subscription,
    SubscriptionStep,
    SubscriptionTask,
)

# 全局使用的mock
run_task = mock.patch("apps.backend.subscription.tasks.run_subscription_task").start()


class TestSubscription(TestCase):
    """
    测试订阅相关的接口
    """

    client = Client()

    def _test_create_subscription(self):
        r = self.client.post(
            path="/backend/api/subscription/create/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "scope": {"bk_biz_id": 2, "node_type": "TOPO", "object_type": "SERVICE", "nodes": [{"id": 123}]},
                    "steps": [
                        {
                            "id": "my_first",
                            "type": "PLUGIN",
                            "config": {
                                "plugin_name": "mysql_exporter",
                                "plugin_version": "2.3",
                                "config_templates": [
                                    {"name": "config.yaml", "version": "2"},
                                    {"name": "env.yaml", "version": "2"},
                                ],
                            },
                            "params": {"url": "asdfasdfs"},
                        }
                    ],
                }
            ),
        )
        assert r.status_code == 200
        assert r.data["result"]

        subscription_id = r.data["data"]["subscription_id"]

        # 探测数据库是否创建了对应的记录
        Subscription.objects.get(id=r.data["data"]["subscription_id"])
        SubscriptionStep.objects.get(step_id="my_first", subscription_id=subscription_id)

        return subscription_id

    def _test_get_subscription(self, subscription_id):
        r = self.client.post(
            path="/backend/api/subscription/info/",
            content_type="application/json",
            data=json.dumps(
                {"bk_username": "admin", "bk_app_code": "blueking", "subscription_id_list": [subscription_id]}
            ),
        )

        assert r.status_code == 200
        assert r.data["result"]

        assert len(r.data["data"]) == 1
        for subscription in r.data["data"]:
            assert isinstance(subscription["scope"], dict)
            assert isinstance(subscription["steps"], list)

    def _test_update_subscription(self, subscription_id):
        r = self.client.post(
            path="/backend/api/subscription/update/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "subscription_id": subscription_id,
                    "scope": {"node_type": "INSTANCE", "nodes": [{"bk_host_id": 100}]},
                    "steps": [
                        {
                            "id": "my_first",
                            "params": {
                                "--web.listen-host": "${cmdb_instance.host}",
                                "--web.listen-port": "${cmdb_instance.port}",
                            },
                        }
                    ],
                }
            ),
        )

        assert r.status_code == 200
        assert r.data["result"]

        subscription = Subscription.objects.get(id=subscription_id)
        step = subscription.steps[0]

        assert subscription.node_type == "INSTANCE"
        assert subscription.nodes[0]["bk_host_id"] == 100
        assert step.params["--web.listen-host"] == "${cmdb_instance.host}"
        assert step.params["--web.listen-port"] == "${cmdb_instance.port}"

    def _test_switch_subscription(self, subscription_id):
        # 测试停用
        r = self.client.post(
            path="/backend/api/subscription/switch/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "subscription_id": subscription_id,
                    "action": "disable",
                }
            ),
        )

        assert r.status_code == 200
        assert r.data["result"]

        subscription = Subscription.objects.get(id=subscription_id)
        assert not subscription.enable

        # 测试启用
        r = self.client.post(
            path="/backend/api/subscription/switch/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "subscription_id": subscription_id,
                    "action": "enable",
                }
            ),
        )

        assert r.status_code == 200
        assert r.data["result"]

        subscription = Subscription.objects.get(id=subscription_id)
        assert subscription.enable

    def test_subscription_change(self):
        subscription_id = self._test_create_subscription()
        self._test_get_subscription(subscription_id)
        self._test_update_subscription(subscription_id)
        self._test_switch_subscription(subscription_id)

    def _test_run_subscription(self):
        run_task.apply_async.call_count = 0
        GsePluginDesc.objects.create(
            **{
                "name": "mysql_exporter",
                "description": "测试插件啊",
                "scenario": "测试",
                "category": "external",
                "launch_node": "all",
                "config_file": "config.yaml",
                "config_format": "yaml",
                "use_db": False,
            }
        )
        pac = Packages(
            pkg_name="test1.tar",
            version="2.3",
            module="gse_plugin",
            project="mysql_exporter",
            pkg_size=10255,
            pkg_path="/data/bkee/miniweb/download/windows/x86_64",
            location="http://127.0.0.1/download/windows/x86_64",
            md5="a95c530a7af5f492a74499e70578d150",
            pkg_ctime="2019-05-05 11:54:28.070771",
            pkg_mtime="2019-05-05 11:54:28.070771",
            os="windows",
            cpu_arch="x86_64",
            is_release_version=False,
            is_ready=True,
        )
        pac.save()
        PluginConfigTemplate.objects.create(
            plugin_name="mysql_exporter",
            plugin_version="*",
            name="config.yaml",
            version="2.3",
            format="yaml",
            file_path="etc",
            content="sss",
            is_release_version=0,
            creator="admin",
            create_time="2019-06-25 15:26:25.051187",
            source_app_code="bk_monitor",
        )
        PluginConfigTemplate.objects.create(
            plugin_name="mysql_exporter",
            plugin_version="*",
            name="env.yaml",
            version="2.3",
            format="yaml",
            file_path="etc",
            content="sss",
            is_release_version=0,
            creator="admin",
            create_time="2019-06-25 15:26:25.051187",
            source_app_code="bk_monitor",
        )
        ProcControl.objects.create(
            id=142,
            module="gse_plugin",
            project="exp_1123",
            plugin_package_id=pac.id,
            install_path="/ usr / local / gse",
            log_path="/ var / log / gse",
            data_path="/ var / lib / gse",
            pid_path="/ var / run / gse / exp_1123.pid",
            start_cmd="./ start.sh",
            stop_cmd="./ stop.sh",
            restart_cmd="./ restart.sh",
            reload_cmd="./ reload.sh",
            kill_cmd="./kill.sh",
            version_cmd="cat VERSION",
            health_cmd="./heath.sh",
            debug_cmd="./ debug.sh",
            os="linux",
            process_name="",
            port_range="1-65535",
            need_delegate=True,
        )
        host = Host(
            bk_host_id=1,
            bk_biz_id=2,
            bk_cloud_id=0,
            inner_ip="10.0.1.10",
            outer_ip=None,
            login_ip="10.0.1.10",
            data_ip="10.0.1.10",
            os_type="WINDOWS",
            node_type="AGENT",
            ap_id=DEFAULT_AP_ID,
        )
        host.save()
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = {
            "count": 1,
            "info": [
                {
                    "host": {
                        "bk_cpu": 4,
                        "bk_isp_name": "1",
                        "bk_os_name": "linux centos",
                        "bk_province_name": "440000",
                        "bk_host_id": 1,
                        "import_from": "2",
                        "bk_os_version": "7.4.1708",
                        "bk_disk": 245,
                        "operator": "",
                        "docker_server_version": "1.12.4",
                        "create_time": "2019-05-17T12:40:29.212+08:00",
                        "bk_mem": 15886,
                        "bk_host_name": "VM_1_10_centos",
                        "last_time": "2019-05-17T15:53:10.164+08:00",
                        "bk_host_innerip": "10.0.1.10",
                        "bk_comment": "",
                        "docker_client_version": "1.12.4",
                        "bk_os_bit": "64-bit",
                        "bk_outer_mac": "",
                        "bk_asset_id": "",
                        "bk_service_term": None,
                        "bk_cloud_id": [
                            {
                                "bk_obj_name": "",
                                "id": "0",
                                "bk_obj_id": "plat",
                                "bk_obj_icon": "",
                                "bk_inst_id": 0,
                                "bk_inst_name": "default area",
                            }
                        ],
                        "bk_sla": None,
                        "bk_cpu_mhz": 1999,
                        "bk_host_outerip": "",
                        "bk_state_name": "CN",
                        "bk_os_type": "1",
                        "bk_mac": "52:54:00:0a:ac:26",
                        "bk_bak_operator": "",
                        "bk_supplier_account": "0",
                        "bk_sn": "",
                        "bk_cpu_module": "AMD EPYC Processor",
                    },
                    "set": [],
                    "biz": [],
                    "module": [],
                }
            ],
        }
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        class host_status(object):
            id = 324
            bk_host_id = 1
            name = "exp_1123"
            status = "RUNNING"
            is_auto = "AUTO"
            version = 3.3
            proc_type = "AGENT"
            configs = [
                {
                    "instance_id": 206,
                    "content": "# \u901a\u7528\u914d\u7f6e\nGSE_AGENT_HOME: /usr/local/gse\nBK_PLUGIN_LOG_PATH: "
                    "u53c2\u6570\nBK_CMD_ARGS: --web.listen-address127.0.0",
                    "file_path": "/usr/test",
                    "name": "test",
                }
            ]
            listen_ip = "127.0.0.1"
            listen_port = 9947
            setup_path = "/ usr / local / gse / external_plugins / sub_458_service_31 / exp_1123"
            log_path = "/ var / log / gse / sub_458_service_31"
            data_path = "/ var / lib / gse / sub_458_service_31"
            pid_path = "/ var / run / gse / sub_458_service_31 / exp_1123.pid"
            group_id = "sub_458_service_31"
            source_type = "subscription"
            source_id = 458
            host_info = {"ip": "10.0.1.10", "bk_supplier_id": "0", "bk_cloud_id": "0"}

            class package(object):
                id = 154
                pkg_name = "exp_1123 - 3.3.tgz"
                version = 3.3
                module = "gse_plugin"
                project = "exp_1123"
                pkg_size = 3969855
                pkg_path = "/ data / bkee / miniweb / download / linux / x86_64"
                md5 = "a433b7ec7e594b34e3ea912e17a98bed"
                pkg_mtime = "2019 - 07 - 23 17:06:51.974803"
                pkg_ctime = "2019 - 07 - 23 17:06:51.974803"
                location = "http: // 10.0.1.10 / download / linux / x86_64"
                os = "windows"
                cpu_arch = "x86_64"
                is_release_version = True
                is_ready = True

                class proc_control(object):
                    id = 142
                    module = "gse_plugin"
                    project = "exp_1123"
                    plugin_package_id = 154
                    install_path = "/ usr / local / gse"
                    log_path = "/ var / log / gse"
                    data_path = "/ var / lib / gse"
                    pid_path = "/ var / run / gse / exp_1123.pid"
                    start_cmd = "./ start.sh"
                    stop_cmd = "./ stop.sh"
                    restart_cmd = "./ restart.sh"
                    reload_cmd = "./ reload.sh"
                    kill_cmd = None
                    version_cmd = "cat VERSION"
                    health_cmd = None
                    debug_cmd = "./ debug.sh"
                    os = "linux"
                    process_name = None
                    port_range = None
                    need_delegate = True

                class plugin_desc(object):
                    id = 83
                    name = "exp_1123"
                    description = "exp_1123"
                    scenario = None
                    description_en = "exp_1123"
                    scenario_en = None
                    category = "external"
                    launch_node = all
                    config_file = None
                    config_format = None
                    use_db = False
                    auto_launch = False
                    is_binary = False

        manager = PluginManager(host_status=host_status, username="admin")
        plugin_manager = mock.patch("apps.backend.plugin.manager.PluginManager").start()
        plugin_manager.return_value = manager

        r = self.client.post(
            path="/backend/api/subscription/create/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "scope": {
                        "bk_biz_id": 2,
                        "node_type": "TOPO",
                        "object_type": "HOST",
                        "nodes": [
                            {
                                "ip": "10.0.1.10",
                                "bk_cloud_id": 0,
                                "bk_supplier_id": 0,
                                "bk_obj_id": "biz",
                                "bk_inst_id": 32,
                            }
                        ],
                    },
                    "steps": [
                        {
                            "id": "my_first",
                            "type": "PLUGIN",
                            "config": {
                                "plugin_name": "mysql_exporter",
                                "plugin_version": "2.3",
                                "config_templates": [
                                    {"name": "config.yaml", "version": "2"},
                                    {"name": "env.yaml", "version": "2"},
                                ],
                            },
                            "params": {"url": "asdfasdfs"},
                        }
                    ],
                }
            ),
        )

        subscription_id = r.data["data"]["subscription_id"]
        # 确认创建订阅步骤
        SubscriptionStep.objects.get(subscription_id=subscription_id)

        status = ProcessStatus(
            id=324,
            name="mysql_exporter",
            status="RUNNING",
            is_auto="AUTO",
            version=3.3,
            proc_type="AGENT",
            configs=[
                {
                    "instance_id": 206,
                    "content": "# \u901a\u7528\u914d\u7f6e\nGSE_AGENT_HOME: /usr/local/gse\nBK_PLUGIN_LOG_PATH: "
                    "u53c2\u6570\nBK_CMD_ARGS: --web.listen-address127.0.0",
                    "file_path": "/usr/test",
                    "name": "test",
                }
            ],
            listen_ip="127.0.0.1",
            listen_port=9947,
            setup_path="/usr/local/gse/external_plugins/sub_458_service_31/exp_1123",
            log_path="/var/log/gse/sub_458_service_31",
            data_path="/var/lib/gse/sub_458_service_31",
            pid_path="/var/run/gse/sub_458_service_31/exp_1123.pid",
            group_id="sub_458_service_31",
            source_type="subscription",
            source_id=subscription_id,
            bk_host_id=host.bk_host_id,
        )
        status.save()

        r = self.client.post(
            path="/backend/api/subscription/run/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    # "scope": {
                    #     "node_type": "INSTANCE",
                    #     "nodes": [
                    #         {
                    #             "ip": "10.0.1.10",
                    #             "bk_cloud_id": "0",
                    #             "bk_supplier_id": "0",
                    #             "bk_obj_id": 'biz',
                    #             "bk_inst_id": 32
                    #         }
                    #     ]
                    # },
                    # "actions": {
                    #     "my_first": "INSTALL"
                    # },
                    "subscription_id": subscription_id,
                }
            ),
        )
        # self.assertEqual(run_task.apply_async.call_count, 1)
        # 确认订阅任务创建
        task = SubscriptionTask.objects.get(subscription_id=subscription_id)
        # Host已存在bk_host_id优先用于生成实例id
        assert task.actions["host|instance|host|1"]["my_first"] == "INSTALL"
        task_id = r.data["data"]["task_id"]
        return subscription_id, task_id

    def _test_task_result(self, subscription_id, task_id):
        r = self.client.post(
            path="/backend/api/subscription/task_result/",
            content_type="application/json",
            data=json.dumps(
                {
                    "bk_username": "admin",
                    "bk_app_code": "blueking",
                    "subscription_id": subscription_id,
                    "task_id_list": [task_id],
                }
            ),
        )

        self.assertEqual(len(r.data["data"]), 1)
        data = r.data["data"][0]
        self.assertEqual(data["instance_id"], "host|instance|host|1")

    def _test_instance_status(self, subscription_id):
        cmdb_client = mock.patch("apps.backend.subscription.tools.client_v2").start()
        cmdb_client.cc.search_host.return_value = SEARCH_HOST
        cmdb_client.cc.search_biz_inst_topo.return_value = TOPO_TREE

        get_process_by_host_id = mock.patch("apps.backend.subscription.tools.get_process_by_host_id").start()
        get_process_by_host_id.return_value = defaultdict(dict)

        r = self.client.post(
            path="/backend/api/subscription/instance_status/",
            content_type="application/json",
            data=json.dumps(
                {"subscription_id_list": [subscription_id], "bk_username": "admin", "bk_app_code": "blueking"}
            ),
        )
        self.assertEqual(r.data["data"][0]["subscription_id"], subscription_id)

    def test_run_task(self):
        subscription_id, task_id = self._test_run_subscription()
        self._test_task_result(subscription_id, task_id)
        self._test_instance_status(subscription_id)

    def test_delete_subscription(self):
        subscription_id = self._test_create_subscription()

        subscription = Subscription.objects.get(id=subscription_id)
        self.assertEqual(subscription.is_deleted, False)

        r = self.client.post(
            path="/backend/api/subscription/delete/",
            content_type="application/json",
            data=json.dumps({"bk_username": "admin", "bk_app_code": "blueking", "subscription_id": subscription_id}),
        )

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["result"], True)

        subscription = Subscription.objects.get(id=subscription_id)
        self.assertEqual(subscription.is_deleted, True)
