# -*- coding: utf-8 -*-
import time
import random
import ntpath
import posixpath

from django.conf import settings
from django.db.models import Max, Subquery
from django.utils.translation import ugettext as _

from apps.backend.components.collections.agent import (
    ChooseAccessPointComponent,
    ConfigurePolicyComponent,
    GetAgentStatusComponent,
    InstallComponent,
    OperatePluginComponent,
    PushUpgradePackageComponent,
    QueryTjjPasswordComponent,
    RegisterHostComponent,
    RestartComponent,
    RunUpgradeCommandComponent,
    UpdateJobStatusComponent,
    UpdateProcessStatusComponent,
    WaitComponent,
    CheckAgentStatusComponent,
    RenderAndPushGseConfigComponent,
    ReloadAgentConfigComponent,
)
from apps.backend.components.collections.job import (
    JobFastExecuteScriptComponent,
    JobFastPushFileComponent,
)
from apps.backend.components.collections.sops import CreateAndStartTaskComponent
from apps.backend.subscription.tools import create_group_id
from apps.node_man import constants as const
from apps.node_man.constants import DEFAULT_SUPPLIER_ID
from apps.node_man.models import Packages, SubscriptionInstanceRecord, Host
from pipeline.builder import ServiceActivity, Var

SCRIPT_TIMEOUT = 3000


class AgentServiceActivity(ServiceActivity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component.inputs.description = Var(type=Var.SPLICE, value="${description}")


class AgentManager(object):
    """
    Agent动作管理
    """

    def __init__(self, instance_record: SubscriptionInstanceRecord, creator: str, blueking_language: str):
        self.host_info = instance_record.instance_info["host"]
        self.creator = creator
        self.blueking_language = blueking_language

    def register_host(self):
        """
        注册主机
        """
        act = AgentServiceActivity(component_code=RegisterHostComponent.code, name=RegisterHostComponent.name)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.bk_host_id = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def query_tjj_password(self):
        """
        查询铁将军密码
        """
        # 验证类型为tjj第一步骤先查询密码
        act = AgentServiceActivity(component_code=QueryTjjPasswordComponent.code, name=QueryTjjPasswordComponent.name,)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.creator = Var(type=Var.PLAIN, value=self.creator)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def choose_ap(self):
        """
        自动选择接入点
        """
        # 若主机未明确选择接入点，则自动进行接入点选择
        act = AgentServiceActivity(
            component_code=ChooseAccessPointComponent.code, name=ChooseAccessPointComponent.name,
        )
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def configure_policy(self):
        """
        开通网络策略
        """
        act = AgentServiceActivity(component_code=ConfigurePolicyComponent.code, name=ConfigurePolicyComponent.name,)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def install(self, name=InstallComponent.name):
        """
        执行安装脚本
        """
        act = AgentServiceActivity(component_code=InstallComponent.code, name=name)
        act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.creator)
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.success_callback_step = Var(type=Var.PLAIN, value="check_deploy_result")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def uninstall_agent(self):
        """
        执行卸载AGENT脚本
        """
        act = AgentServiceActivity(component_code=InstallComponent.code, name=_("卸载Agent"))
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.is_uninstall = Var(type=Var.PLAIN, value=True)
        act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.creator)
        act.component.inputs.success_callback_step = Var(type=Var.PLAIN, value="remove_agent")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def uninstall_proxy(self):
        """
        执行卸载PROXY脚本
        """
        act = AgentServiceActivity(component_code=InstallComponent.code, name=_("卸载Proxy"))
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.is_uninstall = Var(type=Var.PLAIN, value=True)
        act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.creator)
        act.component.inputs.success_callback_step = Var(type=Var.PLAIN, value="remove_proxy")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def push_upgrade_package(self):
        """
        下发升级包
        """
        os_type = const.OS_TYPE.get(str(self.host_info.get("bk_os_type")))
        if not os_type:
            os_type = Host.objects.get(bk_host_id=self.host_info["bk_host_id"]).os_type
        act = AgentServiceActivity(component_code=PushUpgradePackageComponent.code, name=_("下发升级包"))
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": os_type.lower(),
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def run_upgrade_command(self):
        os_type = const.OS_TYPE.get(str(self.host_info.get("bk_os_type")))
        if not os_type:
            os_type = Host.objects.get(bk_host_id=self.host_info["bk_host_id"]).os_type
        act = AgentServiceActivity(component_code=RunUpgradeCommandComponent.code, name=_("执行升级脚本"))
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": os_type.lower(),
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.script_param = Var(type=Var.PLAIN, value="")
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.package_name = Var(type=Var.SPLICE, value="${package_name}")
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def restart(self):
        """
        重启
        """
        act = AgentServiceActivity(component_code=RestartComponent.code, name=RestartComponent.name)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.bk_username = Var(type=Var.PLAIN, value=settings.SYSTEM_USE_API_ACCOUNT)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def wait(self, sleep_time):
        act = AgentServiceActivity(component_code=WaitComponent.code, name=WaitComponent.name)
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.sleep_time = Var(type=Var.PLAIN, value=sleep_time)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def get_agent_status(self, expect_status, name=GetAgentStatusComponent.name):
        """
        查询Agent状态
        """
        act = AgentServiceActivity(component_code=GetAgentStatusComponent.code, name=name)
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.expect_status = Var(type=Var.PLAIN, value=expect_status)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def check_agent_status(self, name=CheckAgentStatusComponent.name):
        """
        查询Agent状态是否正常
        """
        act = AgentServiceActivity(component_code=CheckAgentStatusComponent.code, name=name)
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def update_process_status(self, status, name=UpdateProcessStatusComponent.name):
        """
        查询Agent状态
        """
        act = AgentServiceActivity(component_code=UpdateProcessStatusComponent.code, name=name)
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.status = Var(type=Var.PLAIN, value=status)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def update_job_status(self):
        act = AgentServiceActivity(component_code=UpdateJobStatusComponent.code, name=UpdateJobStatusComponent.name,)
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def push_files_to_proxy(self, files, name=_("下发NGINX安装包")):
        """
        下发NGINX安装包
        """
        file_source = [
            {
                "files": [f"{settings.NGINX_DOWNLOAD_PATH}/{file}" for file in files],
                "account": "root",
                "ip_list": [{"ip": settings.BKAPP_LAN_IP, "bk_cloud_id": 0}],
            }
        ]
        act = AgentServiceActivity(component_code=JobFastPushFileComponent.code, name=name)
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": "linux",
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.file_target_path = Var(type=Var.PLAIN, value=settings.NGINX_DOWNLOAD_PATH)
        act.component.inputs.file_source = Var(type=Var.PLAIN, value=file_source)
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def start_nginx(self):
        script_content = """
/opt/nginx-portable/nginx-portable stop || :;
rm -rf /opt/nginx-portable/;
rm -rf /opt/py36/;
tar xvf %(nginx_path)s/py36.tgz -C /opt;
tar xvf %(nginx_path)s/nginx-portable.tgz -C /opt;
user=nobody
group=nobody
#create group if not exists
egrep "^$group" /etc/group >& /dev/null
if [ $? -ne 0 ]
then
    groupadd $group
fi

#create user if not exists
egrep "^$user" /etc/passwd >& /dev/null
if [ $? -ne 0 ]
then
    useradd -g $group $user
fi
echo -e "
events {
    worker_connections  65535;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    server {
        listen 17980;
        server_name localhost;
        root %(nginx_path)s;

        location / {
            index index.html;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
    server {
        listen 17981;
        server_name localhost;
        resolver `echo $(awk 'BEGIN{ORS=" "} $1=="nameserver" {print $2}' /etc/resolv.conf)`;
        proxy_connect;
        proxy_connect_allow 443 563;
        location / {
            proxy_pass http://\\$http_host\\$request_uri;
        }
    }
}" > /opt/nginx-portable/conf/nginx.conf;
/opt/nginx-portable/nginx-portable start;
sleep 5
is_port_listen_by_pid () {
    local pid regex ret
    pid=$1
    shift 1
    ret=0

    for i in {0..10}; do
        sleep 1
        for port in "$@"; do
            stat -L -c %%i /proc/"$pid"/fd/* 2>/dev/null | grep -qwFf - \
            <( awk -v p="$port" 'BEGIN{ check=sprintf(":%%04X0A$", p)} $2$4 ~ check {print $10}' \
            /proc/net/tcp) || ((ret+=1))
        done
    done
    return "$ret"
}
pid=$(cat /opt/nginx-portable/logs/nginx.pid);
is_port_listen_by_pid "$pid" 17980 17981
exit $?
        """ % {
            "nginx_path": settings.NGINX_DOWNLOAD_PATH
        }
        act = AgentServiceActivity(component_code=JobFastExecuteScriptComponent.code, name=_("启动 NGINX 服务"))
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": "linux",
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.script_content = Var(type=Var.PLAIN, value=script_content)
        act.component.inputs.script_param = Var(type=Var.PLAIN, value="")
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=SCRIPT_TIMEOUT)
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def _operate_process(
        self, action, plugin_name, node, component_code, act_name, error_ignorable=False, context=None,
    ):
        """
        :param action:
        :param plugin_name:
        :param node: {'instance_info': {'os_type': 'linux'}, 'bk_cloud_id':0, 'ip': '127.0.0.1'}
        :param component_code:
        :param act_name:
        :param error_ignorable:
        :param context:
        :return:
        """
        newest = (
            Packages.objects.filter(project=plugin_name, cpu_arch=const.CpuType.x86_64)
            .values("os")
            .annotate(max_id=Max("id"))
        )

        packages = Packages.objects.filter(id__in=Subquery(newest.values("max_id")))

        package_by_os = {package.os: package for package in packages}
        package = package_by_os[node["instance_info"]["os_type"].lower()]
        control = package.proc_control
        control = {
            "start_cmd": control.start_cmd,
            "stop_cmd": control.stop_cmd,
            "restart_cmd": control.restart_cmd,
            "reload_cmd": control.reload_cmd or self.control.restart_cmd,
            "kill_cmd": control.kill_cmd,
            "version_cmd": control.version_cmd,
            "health_cmd": control.health_cmd,
        }

        gse_client = dict(username=self.creator, os_type=package.os)
        host_info = {key: value for key, value in node.items() if key in ("bk_cloud_id", "ip")}
        host_info["bk_supplier_id"] = DEFAULT_SUPPLIER_ID

        if package.os == const.PluginOsType.windows:
            path_handler = ntpath
        else:
            path_handler = posixpath

        if package.plugin_desc.category == const.CategoryType.external:
            # 如果为 external 插件，需要补上插件组目录
            group_id = create_group_id(action.step.subscription, action.instance_record.instance_info)

            setup_path = path_handler.join(
                package.proc_control.install_path, "external_plugins", group_id, package.project,
            )
            pid_path_prefix, pid_filename = path_handler.split(package.proc_control.pid_path)
            pid_path = path_handler.join(pid_path_prefix, group_id, pid_filename)
        else:
            setup_path = path_handler.join(package.proc_control.install_path, "plugins", "bin")
            pid_path = package.proc_control.pid_path

        act = AgentServiceActivity(component_code=component_code, name=act_name, error_ignorable=error_ignorable,)
        act.component.inputs.gse_client = Var(type=Var.PLAIN, value=gse_client)
        act.component.inputs.hosts = Var(type=Var.PLAIN, value=[host_info])
        act.component.inputs.control = Var(type=Var.PLAIN, value=control)
        act.component.inputs.setup_path = Var(type=Var.PLAIN, value=setup_path)
        act.component.inputs.pid_path = Var(type=Var.PLAIN, value=pid_path)
        act.component.inputs.proc_name = Var(type=Var.PLAIN, value=plugin_name)
        act.component.inputs.exe_name = Var(type=Var.PLAIN, value=plugin_name)
        act.component.inputs.context = Var(type=Var.PLAIN, value=context)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)

        return act

    def delegate_plugin(self, plugin_name):
        """
        托管插件
        """
        act = AgentServiceActivity(
            component_code=OperatePluginComponent.code, name=_("托管 {plugin_name} 插件进程").format(plugin_name=plugin_name)
        )
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.action = Var(type=Var.PLAIN, value="delegate")
        act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.creator)
        act.component.inputs.plugin_name = Var(type=Var.PLAIN, value=plugin_name)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def render_and_push_gse_config(self, name=RenderAndPushGseConfigComponent.name):
        """
        渲染并下载agent配置
        """
        os_type = const.OS_TYPE.get(str(self.host_info.get("bk_os_type")))
        act = AgentServiceActivity(component_code=RenderAndPushGseConfigComponent.code, name=name)
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": os_type.lower(),
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.bk_host_id = Var(type=Var.SPLICE, value="${bk_host_id}")
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def reload_agent(self):
        """
        重载agent
        """
        os_type = const.OS_TYPE.get(str(self.host_info.get("bk_os_type")))
        act = AgentServiceActivity(component_code=ReloadAgentConfigComponent.code, name=ReloadAgentConfigComponent.name)
        act.component.inputs.job_client = Var(
            type=Var.PLAIN,
            value={
                "bk_biz_id": self.host_info["bk_biz_id"],
                "username": settings.SYSTEM_USE_API_ACCOUNT,
                "os_type": os_type.lower(),
            },
        )
        act.component.inputs.ip_list = Var(
            type=Var.PLAIN,
            value=[{"ip": self.host_info["bk_host_innerip"], "bk_cloud_id": self.host_info["bk_cloud_id"]}],
        )
        act.component.inputs.host_info = Var(type=Var.PLAIN, value=self.host_info)
        act.component.inputs.script_param = Var(type=Var.PLAIN, value="")
        act.component.inputs.script_timeout = Var(type=Var.PLAIN, value=300)
        act.component.inputs.context = Var(type=Var.PLAIN, value="")
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act

    def configure_sy_policy(self):
        """
        上云环境配置策略
        """
        act = AgentServiceActivity(component_code=CreateAndStartTaskComponent.code, name=_("开通策略"))
        act.component.inputs.sops_client = Var(
            type=Var.PLAIN,
            # 此处为请求ee环境标准运维使用参数
            value={
                "bk_app_code": settings.BKAPP_REQUEST_EE_SOPS_APP_CODE,
                "bk_app_secret": settings.BKAPP_REQUEST_EE_SOPS_APP_SECRET,
                "sops_api_host": settings.BKAPP_EE_SOPS_API_HOST,
                "default": False,
                "bk_biz_id": settings.BKAPP_REQUEST_EE_SOPS_BK_BIZ_ID,
                "username": settings.BKAPP_REQUEST_EE_SOPS_OPERATOR,
            },
        )
        # 作业名称
        name = "【正式环境】gse外网集群添加IP白名单_{}{}{}".format(
            time.strftime("%Y%m%d"), random.randint(10000, 99999), "".join(random.sample(str(int(time.time())), 3))
        )
        act.component.inputs.name = Var(type=Var.PLAIN, value=name)
        act.component.inputs.ip_list = Var(type=Var.PLAIN, value=self.host_info.get("bk_host_outerip"))
        act.component.inputs.template_id = Var(type=Var.PLAIN, value=settings.BKAPP_EE_SOPS_TEMPLATE_ID)
        act.component.inputs.blueking_language = Var(type=Var.PLAIN, value=self.blueking_language)
        return act
