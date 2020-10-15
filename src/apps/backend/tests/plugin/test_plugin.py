# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import shutil
import tarfile
import uuid

import mock
import ujson as json
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase

from apps.backend.plugin.manager import PluginManager
from apps.backend.plugin.tasks import export_plugin, package_task, run_pipeline
from apps.node_man.models import (
    GsePluginDesc,
    Host,
    Packages,
    PipelineTree,
    PluginConfigTemplate,
    ProcControl,
    UploadPackage,
)

# 全局使用的mock
mock.patch("apps.backend.plugin.tasks.export_plugin", delay=export_plugin).start()
mock.patch("apps.backend.plugin.tasks.package_task", delay=package_task).start()
mock.patch("apps.backend.plugin.tasks.run_pipeline.delay", delay=run_pipeline).start()


class PluginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        GsePluginDesc.objects.create(
            **{
                "name": "test1",
                "description": "测试插件啊",
                "scenario": "测试",
                "category": "external",
                "launch_node": "all",
                "config_file": "config.yaml",
                "config_format": "yaml",
                "use_db": False,
            }
        )

        Packages.objects.create(
            pkg_name="test1.tar",
            version="1.0.1",
            module="gse_plugin",
            project="test1",
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

    def test_one(self):
        assert GsePluginDesc.objects.all().count() == 1

    def test_two(self):
        pass


class TestPackageFunction(TestCase):
    temp_path = os.path.join("/tmp", uuid.uuid4().hex)
    tarfile_name = "tarfile.tgz"
    tarfile_path = os.path.join(temp_path, tarfile_name)

    plugin_name = "test_plugin"
    test_client = Client()

    def setUp(self):
        """测试启动初始化配置"""
        # 1. 准备一个yaml配置文件
        config_content = """
  name: "test_plugin"
  version: "1.0.1"
  description: "⽤用于采集主机基础性能数据，包含CPU,内存，磁盘，⽹网络等数据"
  description_en: "⽤用于采集主机基础性能数据，包含CPU,内存，磁盘，⽹网络等数据"
  scenario: "CMDB上的是实时数据，蓝鲸监控-主机监控中的基础性能数据"
  scenario_en: "CMDB上的是实时数据，蓝鲸监控-主机监控中的基础性能数据"
  category: official
  config_file: basereport.conf
  multi_config: True
  config_file_path: ""
  config_format: yaml
  auto_launch: true
  launch_node: proxy
  upstream:
     bkmetric
  dependences:
     gse_agent: "1.2.0"
     bkmetric: "1.6.0"
  control:
     start: "./start.sh %name"
     stop: "./stop.sh %name"
     restart: "./restart.sh %name"
     version: "./%name -v"
     reload: "./%name -s reload"
     health_check: "./%name -z"
  process_name: "test_process"
"""

        # 2. 创建一个打包文件，包含两层内容，一个linux，一个windows
        temp_file_path = os.path.join(self.temp_path, "temp_folder")
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)
        os.mkdir(temp_file_path)
        for package_os, cpu_arch in (("linux", "x86_64"), ("windows", "x86")):
            current_path = os.path.join(temp_file_path, "external_plugins_{}_{}".format(package_os, cpu_arch))
            os.mkdir(current_path)

            plugin_path = os.path.join(current_path, self.plugin_name)
            os.mkdir(plugin_path)

            f1 = open(os.path.join(plugin_path, "plugin"), "w")
            f1.close()
            f2 = open(os.path.join(plugin_path, "project.yaml"), "w")
            f2.write(config_content)
            f2.close()

        with tarfile.open(self.tarfile_path, "w:gz") as tfile:
            tfile.add(temp_file_path, arcname=".", recursive=True)

        # nginx的模拟路径
        settings.NGINX_DOWNLOAD_PATH = settings.UPLOAD_PATH = self.temp_path

        settings.EXPORT_PATH = self.temp_path

    def tearDown(self):
        """测试清理配置"""

        shutil.rmtree(self.temp_path)

    def test_create_upload_record_and_register(self):
        """测试创建上传包记录功能"""
        UploadPackage.create_record(
            module="gse_plugin",
            file_path=self.tarfile_path,
            md5="abcefg",
            operator="haha_test",
            source_app_code="bk_nodeman",
            file_name="tarfile.tgz",
        )

        # 判断路径的转移登录等是否符合预期
        self.assertEqual(
            UploadPackage.objects.filter(
                file_name=self.tarfile_name, file_path=os.path.join(settings.UPLOAD_PATH, self.tarfile_name),
            ).count(),
            1,
        )
        self.assertTrue(os.path.exists(os.path.join(settings.UPLOAD_PATH, self.tarfile_name)))

        # 测试单独注册插件包功能
        upload_object = UploadPackage.objects.get(file_name=self.tarfile_name)
        package_object_list = upload_object.create_package_records(is_release=True)

        # 判断数量正确
        self.assertEqual(len(package_object_list), 2)

        # 判断写入DB数据正确
        # 1. 进程控制信息
        for package in package_object_list:
            process_control = ProcControl.objects.get(plugin_package_id=package.id)
            self.assertEqual(process_control.os, package.os)
            self.assertEqual(process_control.start_cmd, "./start.sh %name")
            self.assertEqual(
                process_control.install_path, "/usr/local/gse" if package.os != "windows" else r"C:\gse",
            )
            self.assertEqual(process_control.port_range, "")
            self.assertEqual(process_control.process_name, "test_process")

        # 2. 包记录信息（window， linux及版本号）
        Packages.objects.get(
            pkg_name="test_plugin-1.0.1.tgz", os="windows", version="1.0.1", cpu_arch="x86",
        )
        Packages.objects.get(
            pkg_name="test_plugin-1.0.1.tgz", os="linux", version="1.0.1", cpu_arch="x86_64",
        )

        # 3. 验证打包的包目录结构符合预期
        self.assertTrue(os.path.exists("/tmp/test_plugin-1.0.1-windows-x86.tgz"))
        self.assertTrue(os.path.exists("/tmp/test_plugin-1.0.1-linux-x86_64.tgz"))

        with tarfile.open("/tmp/test_plugin-1.0.1-windows-x86.tgz") as linux_tar:
            linux_tar.getmember("external_plugins/%s/project.yaml" % self.plugin_name)
            linux_tar.getmember("external_plugins/%s/plugin" % self.plugin_name)

        # 测试导出的功能
        # 准备一个临时的文件在模拟的nginx路径下
        windows_file_path = os.path.join(settings.NGINX_DOWNLOAD_PATH, "windows", "x86", "test_plugin-1.0.1.tgz")
        linux_file_path = os.path.join(settings.NGINX_DOWNLOAD_PATH, "linux", "x86_64", "test_plugin-1.0.1.tgz")

        if not os.path.exists(os.path.dirname(windows_file_path)):
            os.makedirs(os.path.dirname(windows_file_path))
        if not os.path.exists(os.path.dirname(linux_file_path)):
            os.makedirs(os.path.dirname(linux_file_path))

        shutil.copy("/tmp/test_plugin-1.0.1-windows-x86.tgz", windows_file_path)
        shutil.copy("/tmp/test_plugin-1.0.1-linux-x86_64.tgz", linux_file_path)

    def test_upload_api(self):
        """测试上传文件接口"""

        # 测试上传
        raw_response = self.test_client.post(
            path="/backend/package/upload/",
            data={
                "module": "test_module",
                "md5": "123",
                "bk_username": "admin",
                "bk_app_code": "bk_app_code",
                # nginx追加的内容
                "file_local_path": self.tarfile_path,
                "file_local_md5": "123",
                "file_name": "tarfile.tgz",
                "package_file": tarfile.open(self.tarfile_path),
            },
        )

        response = json.loads(raw_response.content)

        self.assertEqual(raw_response.status_code, 200)
        self.assertTrue(response["result"])

        # 逻辑校验
        self.assertEqual(
            UploadPackage.objects.filter(
                file_name=self.tarfile_name, file_path=os.path.join(settings.UPLOAD_PATH, self.tarfile_name),
            ).count(),
            1,
        )
        self.assertTrue(os.path.exists(os.path.join(settings.UPLOAD_PATH, self.tarfile_name)))

        # 测试注册
        raw_response = self.test_client.post(
            path="/backend/api/plugin/create_register_task/",
            data={
                "file_name": self.tarfile_name,
                "is_release": True,
                "bk_username": "admin",
                "bk_app_code": "bk_app_code",
            },
        )
        response = json.loads(raw_response.content)

        self.assertEqual(raw_response.status_code, 200)
        self.assertTrue(response["result"])

        # 逻辑校验
        # 1. 进程控制信息
        self.assertEqual(ProcControl.objects.all().count(), 2)

        # 2. 包记录信息（window， linux及版本号）
        Packages.objects.get(
            pkg_name="test_plugin-1.0.1.tgz", os="windows", version="1.0.1", cpu_arch="x86",
        )
        Packages.objects.get(
            pkg_name="test_plugin-1.0.1.tgz", os="linux", version="1.0.1", cpu_arch="x86_64",
        )

        # 3. 验证打包的包目录结构符合预期
        self.assertTrue(os.path.exists("/tmp/test_plugin-1.0.1-windows-x86.tgz"))
        self.assertTrue(os.path.exists("/tmp/test_plugin-1.0.1-linux-x86_64.tgz"))

        linux_tar = tarfile.open("/tmp/test_plugin-1.0.1-windows-x86.tgz")
        linux_tar.getmember("external_plugins/%s/project.yaml" % self.plugin_name)
        linux_tar.getmember("external_plugins/%s/plugin" % self.plugin_name)

        # 只有一条对应的desc
        self.assertEqual(GsePluginDesc.objects.filter(name=self.plugin_name).count(), 1)


class TestImportCommand(TestCase):
    temp_path = os.path.join("/tmp", uuid.uuid4().hex)

    def setUp(self):
        # nginx的模拟路径
        settings.NGINX_DOWNLOAD_PATH = settings.UPLOAD_PATH = self.temp_path
        os.mkdir(self.temp_path)

    def tearDown(self):
        shutil.rmtree(self.temp_path)

    def test_import_command(self):
        """测试导入命令"""
        if os.path.exists(settings.BK_OFFICIAL_PLUGINS_INIT_PATH):
            call_command("init_official_plugins")
            self.assertTrue(Packages.objects.all().exists())
            self.assertTrue(UploadPackage.objects.all().exists())
            self.assertTrue(PluginConfigTemplate.objects.all().exists())


class TestPluginManager(TestCase):
    class host_status(object):
        id = 324
        bk_host_id = 1
        host = "10.0.1.10_AGENT_2_0"
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
        setup_path = "/usr/local/gse/external_plugins/sub_458_service_31/exp_1123"
        log_path = "/var/log/gse/sub_458_service_31"
        data_path = "/var/lib/gse/sub_458_service_31"
        pid_path = "/var/run/gse/sub_458_service_31/exp_1123.pid"
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
            pkg_path = "/data/bkee/miniweb/download/linux/x86_64"
            md5 = "a433b7ec7e594b34e3ea912e17a98bed"
            pkg_mtime = "2019-07-23 17:06:51.974803"
            pkg_ctime = "2019-07-23 17:06:51.974803"
            location = "http://10.0.1.10/download/linux/x86_64"
            os = "linux"
            cpu_arch = "x86_64"
            is_release_version = True
            is_ready = True

            class proc_control(object):
                id = 142
                module = "gse_plugin"
                project = "exp_1123"
                plugin_package_id = 154
                install_path = "/usr/local/gse"
                log_path = "/var/log/gse"
                data_path = "/var/lib/gse"
                pid_path = "/var/run/gse/exp_1123.pid"
                start_cmd = "./start.sh"
                stop_cmd = "./stop.sh"
                restart_cmd = "./restart.sh"
                reload_cmd = "./reload.sh"
                kill_cmd = None
                version_cmd = "cat VERSION"
                health_cmd = None
                debug_cmd = "./debug.sh"
                os = "linux"
                process_name = None
                port_range = "1-65535"
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

    IP_LIST = [{"ip": "10.0.1.10", "bk_supplier_id": 0, "bk_cloud_id": 0}]
    Host.objects.get_or_create(bk_host_id=1, inner_ip="10.0.1.10", bk_cloud_id=0, bk_biz_id=2)
    Host.objects.filter(bk_host_id=1).update(ap_id=1)
    plugin_manager = PluginManager(host_status=host_status, username="admin")

    def test_deploy(self):
        act = self.plugin_manager.deploy()
        inputs = act.component.inputs
        print(
            inputs["file_source"].value
            == [
                {
                    "files": ["/data/bkee/miniweb/download/linux/" "x86_64/exp_1123 - 3.3.tgz"],
                    "account": "root",
                    "ip_list": self.IP_LIST,
                }
            ]
        )
        self.assertEqual(inputs["file_target_path"].value, "/tmp/nodeman_upload/")
        self.assertEqual(inputs["ip_list"].value, [self.host_status.host_info])

    def test_install(self):
        act = self.plugin_manager.install()
        inputs = act.component.inputs
        self.assertEqual(
            inputs["script_param"].value,
            "-t external -p /usr/local/gse -n exp_1123 -f"
            " exp_1123 - 3.3.tgz -z /tmp/nodeman_upload/ -m OVERRIDE "
            "-d /tmp -i sub_458_service_31",
        )
        self.assertEqual(inputs["ip_list"].value, self.IP_LIST)
        self.assertEqual(inputs["script_timeout"].value, 3000)

    def test_push_config(self):
        act = self.plugin_manager.push_config()
        inputs = act.component.inputs
        self.assertEqual(
            inputs["file_params"].value,
            [
                {
                    "file_list": [
                        {
                            "content": "# \u901a\u7528\u914d\u7f6e\nGSE_AGENT_HOME: /usr/local/gs"
                            "e\nBK_PLUGIN_LOG_PATH: u53c2\u6570\nBK_CMD_ARGS: --web.listen-address127.0.0",
                            "name": "test",
                        }
                    ],
                    "file_target_path": "/usr/test",
                }
            ],
        )
        self.assertEqual(inputs["ip_list"].value, self.IP_LIST)

    def test_remove_config(self):
        act = self.plugin_manager.remove_config()
        inputs = act.component.inputs
        self.assertEqual(inputs["script_param"].value, "/usr/test/test")
        self.assertEqual(inputs["ip_list"].value, self.IP_LIST)
        self.assertEqual(inputs["script_timeout"].value, 3000)
        self.assertEqual(
            inputs["script_content"].value, '#!/bin/bash\n\necho "remove config files" $@\n\nrm -f $@\n',
        )

    def test_uninstall(self):
        path = os.path.join(os.path.dirname(__file__), "../../plugin/scripts/", "update_binary.sh")
        with open(path) as fh:
            script_content = fh.read()
        act = self.plugin_manager.uninstall()
        inputs = act.component.inputs
        self.assertEqual(
            inputs["script_param"].value, "-t external -p /usr/local/gse -d /tmp -n exp_1123 -r -i sub_458_service_31",
        )
        self.assertEqual(inputs["ip_list"].value, self.IP_LIST)
        self.assertEqual(inputs["script_timeout"].value, 3000)
        self.assertEqual(inputs["script_content"].value, script_content)

    def test_start(self):
        act = self.plugin_manager.start()
        inputs = act.component.inputs
        self.assertEqual(
            inputs["control"].value,
            {
                "start_cmd": self.host_status.package.proc_control.start_cmd,
                "stop_cmd": self.host_status.package.proc_control.stop_cmd,
                "restart_cmd": self.host_status.package.proc_control.restart_cmd,
                "reload_cmd": self.host_status.package.proc_control.reload_cmd,
                "kill_cmd": self.host_status.package.proc_control.kill_cmd,
                "version_cmd": self.host_status.package.proc_control.version_cmd,
                "health_cmd": self.host_status.package.proc_control.health_cmd,
            },
        )
        self.assertEqual(inputs["exe_name"].value, "exp_1123")
        self.assertEqual(
            inputs["setup_path"].value, "/usr/local/gse/external_plugins/sub_458_service_31/exp_1123",
        )
        self.assertEqual(inputs["pid_path"].value, "/var/run/gse/sub_458_service_31/exp_1123.pid")
        self.assertEqual(inputs["proc_name"].value, "sub_458_service_31_exp_1123")
        self.assertEqual(inputs["hosts"].value, self.IP_LIST)
        self.assertEqual(act.component.code, "gse_start_process")

    def test_restart(self):
        act = self.plugin_manager.restart()
        inputs = act.component.inputs
        self.assertEqual(
            inputs["control"].value,
            {
                "start_cmd": self.host_status.package.proc_control.start_cmd,
                "stop_cmd": self.host_status.package.proc_control.stop_cmd,
                "restart_cmd": self.host_status.package.proc_control.restart_cmd,
                "reload_cmd": self.host_status.package.proc_control.reload_cmd,
                "kill_cmd": self.host_status.package.proc_control.kill_cmd,
                "version_cmd": self.host_status.package.proc_control.version_cmd,
                "health_cmd": self.host_status.package.proc_control.health_cmd,
            },
        )
        self.assertEqual(inputs["exe_name"].value, "exp_1123")
        self.assertEqual(
            inputs["setup_path"].value, "/usr/local/gse/external_plugins/sub_458_service_31/exp_1123",
        )
        self.assertEqual(inputs["pid_path"].value, "/var/run/gse/sub_458_service_31/exp_1123.pid")
        self.assertEqual(inputs["proc_name"].value, "sub_458_service_31_exp_1123")
        self.assertEqual(inputs["hosts"].value, self.IP_LIST)
        self.assertEqual(act.component.code, "gse_restart_process")

    def test_stop(self):
        act = self.plugin_manager.stop()
        inputs = act.component.inputs
        self.assertEqual(inputs["proc_name"].value, "sub_458_service_31_exp_1123")
        self.assertEqual(inputs["hosts"].value, self.IP_LIST)
        self.assertEqual(act.component.code, "gse_stop_process")

    def test_reload(self):
        act = self.plugin_manager.reload()
        inputs = act.component.inputs
        self.assertEqual(inputs["proc_name"].value, "sub_458_service_31_exp_1123")
        self.assertEqual(inputs["hosts"].value, self.IP_LIST)
        self.assertEqual(act.component.code, "gse_reload_process")

    def test_allocate_port(self):
        act = self.plugin_manager.allocate_port("127.0.0.1")
        inputs = act.component.inputs
        self.assertEqual(inputs["port_range"].value, self.plugin_manager.control.port_range)
        self.assertEqual(act.component.code, "job_allocate_port")

    def test_debug_and_get_debug_status(self):
        mock.patch("pipeline.service.task_service.get_state", return_value="FINISHED").start()
        origin_install_path = self.plugin_manager.control.install_path
        pipeline_id = self.plugin_manager.debug("/tmp")
        # 由于debug未考虑线程安全，会把install_path修改，影响其它测试用例，此处需把install_path改回
        self.plugin_manager.control.install_path = origin_install_path
        # 确定PipelineTree创建成功
        pipeline = PipelineTree.objects.get(id=pipeline_id)
        status = self.plugin_manager.get_debug_status(pipeline)

        self.assertEqual(len(status), 3)
