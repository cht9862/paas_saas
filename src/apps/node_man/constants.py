# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from apps.utils.basic import choices_to_namedtuple, tuple_choices, dict_to_choices, tuple_to_namedtuple, reverse_dict

# 此值为历史遗留，后续蓝鲸不使用此字段后可废弃
DEFAULT_SUPPLIER_ID = 0

LINUX_SEP = "/"
WINDOWS_SEP = "\\"

########################################################################################################
# 任务超时控制
########################################################################################################
TASK_TIMEOUT = 0  # 脚本超时控制在180s=3min
TASK_MAX_TIMEOUT = 3600  # 脚本超时控制在180s=3min
JOB_MAX_RETRY = 60  # 默认轮询作业最大次数 100次=3min
JOB_SLEEP_SECOND = 3  # 默认轮询作业周期 3s
MAX_POLL_TIMES = JOB_MAX_RETRY
MAX_UNINSTALL_RETRY = JOB_MAX_RETRY

########################################################################################################
# 第三方系统相关配置
########################################################################################################

# 默认云区域ID
DEFAULT_CLOUD = int(os.environ.get("DEFAULT_CLOUD", 0))
# 自动选择接入点ID
DEFAULT_AP_ID = int(os.environ.get("DEFAULT_AP_ID", -1))
# 默认收藏云区域ID列表
DEFAULT_FAVORS = [DEFAULT_CLOUD]
# 作业平台作业成功标志
JOB_SUCCESS = 3

########################################################################################################
# CHOICES
########################################################################################################
AUTH_TUPLE = ("PASSWORD", "KEY", "TJJ_PASSWORD")
AUTH_CHOICES = tuple_choices(AUTH_TUPLE)
AuthType = choices_to_namedtuple(AUTH_CHOICES)

OS_TUPLE = ("LINUX", "WINDOWS", "AIX")
OS_CHOICES = tuple_choices(OS_TUPLE)
OsType = choices_to_namedtuple(OS_CHOICES)
OS_CHN = {"WINDOWS": "Windows", "LINUX": "Linux", "AIX": "Aix"}
BK_OS_TYPE = {"LINUX": "1", "WINDOWS": "2", "AIX": "3"}

OS_TYPE = {"1": "LINUX", "2": "WINDOWS", "3": "AIX"}

NODE_TUPLE = ("AGENT", "PROXY", "PAGENT")
NODE_CHOICES = tuple_choices(NODE_TUPLE)
NodeType = choices_to_namedtuple(NODE_CHOICES)

NODE_FROM_TUPLE = ("CMDB", "EXCEL", "NODE_MAN")
NODE_FROM_CHOICES = tuple_choices(NODE_FROM_TUPLE)
NodeFrom = choices_to_namedtuple(NODE_FROM_CHOICES)

PROC_TUPLE = ("AGENT", "PLUGIN")
PROC_CHOICES = tuple_choices(PROC_TUPLE)
ProcType = choices_to_namedtuple(PROC_CHOICES)

HEAD_TUPLE = ("total_count", "failed_count", "success_count")
HEAD_CHOICES = tuple_choices(HEAD_TUPLE)
HeadType = choices_to_namedtuple(HEAD_CHOICES)

SORT_TUPLE = ("ASC", "DEC")
SORT_CHOICES = tuple_choices(SORT_TUPLE)
SortType = choices_to_namedtuple(SORT_CHOICES)

AGENT_JOB_TUPLE = (
    "INSTALL_PROXY",
    "INSTALL_AGENT",
    "RESTART_PROXY",
    "RESTART_AGENT",
    "REINSTALL_PROXY",
    "REINSTALL_AGENT",
    "REPLACE_PROXY",
    "UNINSTALL_AGENT",
    "REMOVE_AGENT",
    "UNINSTALL_PROXY",
    "UPGRADE_PROXY",
    "UPGRADE_AGENT",
    "IMPORT_PROXY",
    "IMPORT_AGENT",
    "RESTART_AGENT",
    "RESTART_PROXY",
    "RELOAD_AGENT",
    "RELOAD_PROXY",
)
AUTHINFO_JOB_TUPLE = ("UPDATE_AUTHINFO",)
PLUGIN_JOB_TUPLE = (
    "MAIN_START_PLUGIN",
    "MAIN_STOP_PLUGIN",
    "MAIN_RESTART_PLUGIN",
    "MAIN_RELOAD_PLUGIN",
    "MAIN_DELEGATE_PLUGIN",
    "MAIN_UNDELEGATE_PLUGIN",
    "MAIN_INSTALL_PLUGIN",
)
PACKAGE_JOB_TUPLE = ("PACKING_PLUGIN",)

JOB_TUPLE = AGENT_JOB_TUPLE + PLUGIN_JOB_TUPLE + AUTHINFO_JOB_TUPLE + PACKAGE_JOB_TUPLE
JOB_CHOICES = tuple_choices(JOB_TUPLE)
JobType = choices_to_namedtuple(JOB_CHOICES)

JOB_TYPE_DICT = {
    "INSTALL_PROXY": _("安装 Proxy"),
    "INSTALL_AGENT": _("安装 Agent"),
    "RESTART_AGENT": _("重启 Agent"),
    "RESTART_PROXY": _("重启 Proxy"),
    "REPLACE_PROXY": _("替换 Proxy"),
    "REINSTALL_PROXY": _("重装 Proxy"),
    "REINSTALL_AGENT": _("重装 Agent"),
    "UPGRADE_PROXY": _("升级 Proxy"),
    "UPGRADE_AGENT": _("升级 Agent"),
    "REMOVE_AGENT": _("移除 Agent"),
    "UNINSTALL_AGENT": _("卸载 Agent"),
    "UNINSTALL_PROXY": _("卸载 Proxy"),
    # 'UPDATE_CONFIG': _(u"更新配置"),
    "UPDATE_AUTHINFO": _("更新信息"),
    "IMPORT_PROXY": _("导入Proxy机器"),
    "IMPORT_AGENT": _("导入Agent机器"),
    # 'IMPORT_PAGENT': _(u"导入PAGENT机器"),
    "MAIN_START_PLUGIN": _("启动插件"),
    "MAIN_STOP_PLUGIN": _("停止插件"),
    "MAIN_RESTART_PLUGIN": _("重启插件"),
    "MAIN_RELOAD_PLUGIN": _("重载插件"),
    "MAIN_DELEGATE_PLUGIN": _("托管插件"),
    "MAIN_UNDELEGATE_PLUGIN": _("取消托管插件"),
    "MAIN_INSTALL_PLUGIN": _("安装插件"),
    "RELOAD_AGENT": _("重载配置"),
    "RELOAD_PROXY": _("重载配置"),
    # 以下仅为表头【手动安装】做翻译，手动安装时仍传INSTALL_XXX
    "MANUAL_INSTALL_AGENT": _("手动安装 Agent"),
    "MANUAL_INSTALL_PROXY": _("手动安装 Proxy"),
    "PACKING_PLUGIN": _("打包插件"),
}

OP_TYPE_TUPLE = (
    "INSTALL",
    "REINSTALL",
    "UNINSTALL",
    "REMOVE",
    "REPLACE",
    "UPGRADE",
    "UPDATE_AUTHINFO",
    "IMPORT",
    "UPDATE",
    "START",
    "STOP",
    "RELOAD",
    "RESTART",
    "DELEGATE",
    "UNDELEGATE",
    "DEBUG",
)
OP_CHOICES = tuple_choices(OP_TYPE_TUPLE)
OpType = choices_to_namedtuple(OP_CHOICES)

STATUS_TUPLE = ("QUEUE", "RUNNING", "SUCCESS", "FAILED")
STATUS_CHOICES = tuple_choices(STATUS_TUPLE)
StatusType = choices_to_namedtuple(STATUS_CHOICES)

HEAD_PLUGINS = ["basereport", "exceptionbeat", "processbeat", "bkunifylogbeat", "bkmonitorbeat", "gsecmdline"]

IAM_ACTION_DICT = {
    "cloud_view": _("云区域查看"),
    "cloud_edit": _("云区域编辑"),
    "cloud_delete": _("云区域删除"),
    "cloud_create": _("云区域创建"),
    "ap_edit": _("接入点编辑"),
    "ap_delete": _("接入点删除"),
    "ap_create": _("接入点创建"),
    "ap_view": _("接入点查看"),
    "globe_task_config": _("任务配置"),
    "task_history_view": _("任务历史查看"),
    "agent_view": _("agent查询"),
    "agent_operate": _("agent操作"),
    "proxy_operate": _("proxy操作"),
    "plugin_view": _("插件查询"),
    "plugin_operate": _("插件操作"),
}
IAM_ACTION_TUPLE = tuple(IAM_ACTION_DICT.keys())
IAM_ACTION_CHOICES = tuple_choices(IAM_ACTION_TUPLE)
IamActionType = choices_to_namedtuple(IAM_ACTION_CHOICES)


class JobStatusType(object):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PART_FAILED = "PART_FAILED"
    TERMINATED = "TERMINATED"

    @classmethod
    def get_choices(cls):
        return (
            (cls.PENDING, _("等待执行")),
            (cls.RUNNING, _("正在执行")),
            (cls.SUCCESS, _("执行成功")),
            (cls.FAILED, _("执行失败")),
            (cls.PART_FAILED, _("部分失败")),
            (cls.TERMINATED, _("已终止")),
        )


NODE_MAN_LOG_LEVEL = ("INFO", "DEBUG", "PRIMARY", "WARNING", "ERROR")

LEVEL_TUPLE = ("user", "warning", "error", "info", "debug")
LEVEL_CHOICES = tuple_choices(LEVEL_TUPLE)
LevelType = choices_to_namedtuple(LEVEL_CHOICES)

CODE_STATUS_TUPLE = (
    "OK",
    "UNAUTHORIZED",
    "VALIDATE_ERROR",
    "METHOD_NOT_ALLOWED",
    "PERMISSION_DENIED",
    "SERVER_500_ERROR",
    "OBJECT_NOT_EXIST",
    "PARAMS_PARSE_ERROR",
)
CODE_STATUS_CHOICES = tuple_choices(CODE_STATUS_TUPLE)
ResponseCodeStatus = choices_to_namedtuple(CODE_STATUS_CHOICES)

FLAG_TUPLE = ("STEP", "EMPTY")
FLAG_CHOICES = tuple_choices(FLAG_TUPLE)
FlagType = choices_to_namedtuple(FLAG_CHOICES)

CODE_TUPLE = (
    # 任务成功
    "INIT",
    "SUCCESS",
    "STILL_RUNNING",
    "CELERY_TASK_EXCEPT",
    "CELERY_TASK_TIMEOUT",
    "WAIT_AGENT_TIMEOUT",
    "UNEXPECTED_RETURN",
    "CURL_FILE_FAILED",
    "REGISTER_FAILED",
    "START_JOB_FAILED",
    "JOB_TIMEOUT",
    "WAIT_AGENT_FAILED",
    "IJOBS_FAILED",
    "FORCE_STOP",
    "INSTALL_FAILED",
    "UPDATE_CLOUD_AREA",
    "UPDATE_FAILED",
    # SSH认证类错误
    "SSH_LOGIN_TIMEOUT",
    "SSH_WRONG_PASSWORD",
    "SSH_LOGIN_EXCEPT",
    "SSH_LOGIN_KEY_ERR",
    "NOT_SUPPORT_AUTH_WAY",
    "SOCKET_TIMEOUT",
    # WMIEXEC
    "UPLOAD_FAILED",
    "DETECT_ARC_FAILED",
    # 其他错误
    "COMMAND_NOT_FOUND",
    "FILE_DOES_NOT_EXIST",
)
CODE_CHOICES = tuple_choices(CODE_TUPLE)
CodeType = choices_to_namedtuple(CODE_CHOICES)

CODE_DESC_TUPLE = [
    ("INIT", _("初始化")),
    ("SUCCESS", _("成功")),
    ("STILL_RUNNING", _("运行中")),
    ("CELERY_TASK_EXCEPT", _("后台任务异常")),
    ("CELERY_TASK_TIMEOUT", _("后台任务超时")),
    ("WAIT_AGENT_TIMEOUT", _("等待Agent超时")),
    ("UNEXPECTED_RETURN", _("异常返回")),
    ("CURL_FILE_FAILED", _("CURL_FILE_FAILED")),
    ("REGISTER_FAILED", _("注册失败")),
    ("START_JOB_FAILED", _("启动任务失败")),
    ("JOB_TIMEOUT", _("超时退出")),
    ("WAIT_AGENT_FAILED", _("等待Agent超时失败")),
    ("IJOBS_FAILED", _("ijobs作业失败")),
    ("FORCE_STOP", _("强制终止")),
    ("INSTALL_FAILED", _("安装失败")),
    # SSH认证类错误
    ("SSH_LOGIN_TIMEOUT", _("SSH登录超时")),
    ("SSH_WRONG_PASSWORD", _("SSH密码错误")),
    ("SSH_LOGIN_EXCEPT", _("SSH登录错误")),
    ("SSH_LOGIN_KEY_ERR", _("SSH登录错误")),
    ("NOT_SUPPORT_AUTH_WAY", _("不支持的验证方式")),
    ("SOCKET_TIMEOUT", _("链接超时")),
    # WMIEXEC
    ("UPLOAD_FAILED", _("上传失败")),
    ("DETECT_ARC_FAILED", _("DETECT_ARC_FAILED")),
    # 其他错误
    ("COMMAND_NOT_FOUND", _("命令不存在")),
    ("FILE_DOES_NOT_EXIST", _("文件不存在")),
]
CODE_DESC_DICT = OrderedDict(CODE_DESC_TUPLE)

UPDATE_CONFIG_STEP_CHOICES = [
    ("PUSH_CONFIG", _("下发配置")),
    ("REPLACE_CONFIG", _("替换配置")),
]

PLUGIN_JOB_STEP_CHOICES = [
    ("DEBUG_PROCESS", _("调试进程")),
    ("STOP_DEBUG_PROCESS", _("停止调试进程")),
    ("REGISTER_PROCESS", _("注册进程")),
    ("OPERATE_PROCESS", _("操作进程")),
]

UPDATE_BIN_STEP_CHOICES = [
    ("UPLOAD_FILE", _("上传文件")),
    ("OVERWRITE_FILE", _("替换文件")),
    ("RESTART_PROCESS", _("重启进程")),
    ("DELEGATE_PROCESS", _("托管进程")),
]

STEP_CHOICES = (
    UPDATE_CONFIG_STEP_CHOICES
    + [
        ("INIT", _("任务初始化")),
        ("SSH_LOGIN", _("登录目标主机")),
        ("INSTALL_DEP", _("安装基础依赖")),
        ("DOWNLOAD_FILE", _("下载安装包")),
        ("UPLOAD_FILE", _("上传安装包")),
        ("EXECUTE_SCRIPT", _("执行安装脚本")),
        ("EXECUTE_RESTART_SCRIPT", _("执行重启作业")),
        ("SCRIPT_DONE", _("安装脚本执行完毕")),
        ("REGISTER_CMDB", _("注册主机到CMDB")),
        ("UPDATE_CLOUD_AREA", _("更新主机云区域")),
        ("WAIT_AGENT", _("检测Agent状态和版本")),
        ("CREATE_JOB_SCRIPT", _("准备安装脚本")),
        ("CREATE_UNINSTALL_SCRIPT", _("准备卸载脚本")),
        ("EXECUTE_JOB", _("执行批量安装作业")),
        ("EXECUTE_UNINSTALL_JOB", _("执行批量卸载作业")),
        ("DETECT_WIN_ARC", _("检测Windows系统版本")),
        ("OVER_SUCCESS", _("任务执行成功")),
        ("OVER_FAILED", _("任务执行失败")),
    ]
    + PLUGIN_JOB_STEP_CHOICES
    + UPDATE_BIN_STEP_CHOICES
)

JOB_STEP_MAPPING = {
    "UPDATE_PLUGIN": (-4, 0, -3, -2),
    "START_PLUGIN": (-6, -5),
    "STOP_PLUGIN": (-6, -5),
    "RELOAD_PLUGIN": (-6, -5),
    "RESTART_PLUGIN": (-6, -5),
    "DELEGATE_PLUGIN": (-6, -5),
    "UNDELEGATE_PLUGIN": (-6, -5),
    "UPGRADE_PLUGIN": (-4, -3, -2),
}

STEP_DICT = OrderedDict(STEP_CHOICES)
# STEP_DISPLAY = {step[0]: step[1] for i, step in enumerate(STEP_CHOICES)}
STEP_DISPLAY = dict(STEP_CHOICES)
StepType = tuple_to_namedtuple(STEP_DICT.keys())

PROC_STATE_TUPLE = ("RUNNING", "UNKNOWN", "TERMINATED", "NOT_INSTALLED", "UNREGISTER")
PROC_STATE_CHOICES = tuple_choices(PROC_STATE_TUPLE)
ProcStateType = choices_to_namedtuple(PROC_STATE_CHOICES)
PROC_STATUS_DICT = {0: "UNKNOWN", 1: "RUNNING", 2: "TERMINATED", 3: "NOT_INSTALLED"}
PROC_STATUS_CHN = {
    "UNKNOWN": _("未知"),
    "NOT_INSTALLED": _("未安装"),
    "UNREGISTER": _("未注册"),
    "RUNNING": _("正常"),
    "TERMINATED": _("异常"),
    "SUCCESS": _("成功"),
    "FAILED": _("失败"),
    "QUEUE": _("队列中"),
}
PLUGIN_STATUS_DICT = {0: "UNREGISTER", 1: "RUNNING", 2: "TERMINATED"}

AUTO_STATE_TUPLE = ("AUTO", "UNAUTO")
AUTO_STATE_CHOICES = tuple_choices(AUTO_STATE_TUPLE)
AutoStateType = choices_to_namedtuple(AUTO_STATE_CHOICES)
AUTO_STATUS_DICT = {
    0: "UNAUTO",
    1: "AUTO",
}

IPROC_STATE_CHOICES = dict_to_choices(PROC_STATUS_DICT)
IPROC_STATUS_DICT = reverse_dict(PROC_STATUS_DICT)

FUNCTION_TUPLE = ("START", "STOP", "RESTART", "RELOAD", "DELEGATE", "UNDELEGATE")
FUNCTION_CHOICES = tuple_choices(FUNCTION_TUPLE)
FunctionType = choices_to_namedtuple(FUNCTION_CHOICES)

CATEGORY_TUPLE = ("official", "external", "scripts")
CATEGORY_CHOICES = tuple_choices(CATEGORY_TUPLE)
CategoryType = choices_to_namedtuple(CATEGORY_CHOICES)

CATEGORY_LIST = [
    {"id": CategoryType.official, "name": _("官方插件")},
    {"id": CategoryType.external, "name": _("第三方插件")},
    {"id": CategoryType.scripts, "name": _("脚本插件")},
]

FUNCTION_LIST = [
    {"id": FunctionType.START, "name": _("启动")},
    {"id": FunctionType.STOP, "name": _("停止")},
    {"id": FunctionType.RESTART, "name": _("重启")},
    {"id": FunctionType.RELOAD, "name": _("重载")},
    {"id": FunctionType.DELEGATE, "name": _("托管")},
    {"id": FunctionType.UNDELEGATE, "name": _("取消托管")},
]

CONFIG_FILE_FORMAT_TUPLE = ("json", "yaml", "", None)
CONFIG_FILE_FORMAT_CHOICES = tuple_choices(CONFIG_FILE_FORMAT_TUPLE)

PLUGIN_OS_TUPLE = ("windows", "linux", "aix")
PLUGIN_OS_CHOICES = tuple_choices(PLUGIN_OS_TUPLE)
PluginOsType = choices_to_namedtuple(PLUGIN_OS_CHOICES)

CPU_TUPLE = ("x86", "x86_64", "powerpc")
CPU_CHOICES = tuple_choices(CPU_TUPLE)
CpuType = choices_to_namedtuple(CPU_CHOICES)


PACKAGE_PATH_RE = re.compile(
    "(?P<is_external>external_)?plugins_(?P<os>(linux|windows|aix))_(?P<cpu_arch>(x86_64|x86|powerpc|aarch64))"
)

SYNC_CMDB_HOST_CONFIG_KEY = "SYNC_CMDB_HOST_BIZ"

# 周期任务相关
QUERY_EXPIRED_INFO_LENS = 2000
QUERY_AGENT_STATUS_HOST_LENS = 2000
QUERY_PLUGIN_STATUS_HOST_LENS = 2000
QUERY_CMDB_LIMIT = 500
QUERY_CLOUD_LIMIT = 200
VERSION_PATTERN = re.compile(r"[vV]?(\d+\.){1,5}\d+")
WINDOWS_PORT = 445
LINUX_PORT = 22
WINDOWS_ACCOUNT = "Administrator"
LINUX_ACCOUNT = "root"
APPLY_RESOURCE_WATCH_EVENT_LENS = 2000

BIZ_CACHE_SUFFIX = "_biz_cache"
JOB_MAX_VALUE = 100000

# 监听资源类型
RESOURCE_TUPLE = ("host", "host_relation")
RESOURCE_CHOICES = tuple_choices(RESOURCE_TUPLE)
ResourceType = choices_to_namedtuple(RESOURCE_CHOICES)

# APP运行环境
BKAPP_RUN_ENV_TUPLE = ("chuhai", "shangyun", "ee", "ce")
BKAPP_RUN_ENV_CHOICES = tuple_choices(BKAPP_RUN_ENV_TUPLE)
BkappRunEnvType = choices_to_namedtuple(BKAPP_RUN_ENV_CHOICES)
