# -*- coding: utf-8 -*-

from mock import MagicMock

from apps.backend.api.constants import GseDataErrCode


TASK_ID = 10000

GSE_CLIENT_MOCK_PATH = "apps.backend.api.gse.get_client_by_user"


GSE_TASK_RESULT = {
    "success": [
        {
            "content": "",
            "error_code": 0,
            "error_msg": "success",
            "bk_cloud_id": "0",
            "bk_supplier_id": "0",
            "ip": "10.10.1.1",
        }
    ],
    "pending": [],
    "failed": [
        {
            "content": "",
            "error_code": 850,
            "error_msg": "Fail to register, for the process info already exists.",
            "bk_cloud_id": "0",
            "bk_supplier_id": "0",
            "ip": "10.0.0.2",
        }
    ],
}

UPDATE_PROC_INFO_RETURN = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": {
        "0:0:10.10.1.1:nodeman:sub_870_host_1_host_exp001": {
            "error_code": GseDataErrCode.SUCCESS,
            "error_msg": "success",
            "content": "",
        },
        "0:0:10.0.0.2:nodeman:sub_870_host_1_host_exp002": {
            "error_code": GseDataErrCode.ALREADY_REGISTERED,
            "error_msg": "Fail to register, for the process info already exists.",
            "content": "",
        },
    },
}

OPERATE_PROC_RETURN = {"result": True, "code": 0, "message": "success", "data": {"task_id": TASK_ID}}

GET_PROC_OPERATE_RESULT_RETURN = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": {
        "0:0:10.10.1.1:nodeman:sub_870_host_1_host_exp001": {
            "error_code": GseDataErrCode.SUCCESS,
            "error_msg": "success",
            "content": "",
        },
        "0:0:10.0.0.2:nodeman:sub_870_host_1_host_exp002": {
            "error_code": GseDataErrCode.ALREADY_REGISTERED,
            "error_msg": "Fail to register, for the process info already exists.",
            "content": "",
        },
    },
}


class GseMockClient(object):
    def __init__(
        self,
        update_proc_info_return=None,
        unregister_proc_info_return=None,
        operate_proc_return=None,
        get_proc_operate_result_return=None,
    ):
        self.gse = MagicMock()
        self.gse.update_proc_info = MagicMock(return_value=update_proc_info_return)
        self.gse.unregister_proc_info = MagicMock(return_value=unregister_proc_info_return)
        self.gse.operate_proc = MagicMock(return_value=operate_proc_return)
        self.gse.get_proc_operate_result = MagicMock(return_value=get_proc_operate_result_return)
