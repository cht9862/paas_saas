# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _

from apps.component.esbclient import client_v2
from apps.exceptions import ComponentCallError
from apps.node_man.exceptions import (
    CloudNotExistError,
    CloudUpdateAgentError,
    CmdbAddCloudPermissionError,
    BusinessNotPermissionError,
)
from apps.node_man.constants import BIZ_CACHE_SUFFIX, IamActionType
from apps.node_man.handlers.iam import IamHandler
from apps.utils.local import get_request_username
from apps.utils import APIModel
from blueapps.account.models import User
from common.log import logger


class CmdbHandler(APIModel):
    """
    Cmdb处理器
    """

    def cmdb_or_cache_biz(self, username: str):
        """
        如果有缓存，则返回缓存；
        如果没有缓存，则重新调取接口。
        格式:
        [{
            'bk_biz_id': biz_id ,
            'bk_biz_name': bk_biz_name
        }]
        """
        user_biz_cache = cache.get(username + BIZ_CACHE_SUFFIX)

        if user_biz_cache:
            # 如果存在缓存则返回
            return user_biz_cache
        else:
            # 缓存已过期，重新获取
            kwargs = {"fields": ["bk_biz_id", "bk_biz_name"]}

            # 如果不使用权限中心，则需要拿到业务运维
            if not (settings.USE_IAM or User.objects.filter(username=username, is_superuser=True).exists()):
                kwargs["condition"] = {"bk_biz_maintainer": username}

            try:
                # 需要以用户的名字进行请求
                result = client_v2.cc.search_business(kwargs)
                cache.set(username + BIZ_CACHE_SUFFIX, result, 60)
                return result
            except ComponentCallError as e:
                logger.error("esb->call search_business error %s" % e.message)
                return {"info": []}

    def ret_biz_permission(self, param):
        """
        处理业务权限
        :return: 用户有权限的业务列表
        """

        username = get_request_username()
        all_biz = self.cmdb_or_cache_biz(username)["info"]

        # 如果是超管，则返回所有权限
        if IamHandler.is_superuser(username):
            all_biz.insert(0, {"bk_biz_id": settings.BK_CMDB_RESOURCE_POOL_BIZ_ID, "bk_biz_name": "资源池"})
            return all_biz

        # 若使用权限中心
        if settings.USE_IAM:
            all_biz.insert(0, {"bk_biz_id": settings.BK_CMDB_RESOURCE_POOL_BIZ_ID, "bk_biz_name": "资源池"})
            biz_view_permission = IamHandler().fetch_policy(username, [param["action"]])[param["action"]]
            return [
                {"bk_biz_id": biz["bk_biz_id"], "bk_biz_name": biz["bk_biz_name"]}
                for biz in all_biz
                if biz["bk_biz_id"] in biz_view_permission
            ]

        # 若不使用权限中心，cmdb_or_cache_biz默认返回的是业务运维权限
        return all_biz

    def cmdb_biz_inst_topo(self, biz):
        """
        搜索业务的拓扑树
        :return:
        """

        kwargs = {"bk_biz_id": biz}
        try:
            # 需要以用户的名字进行请求
            result = client_v2.cc.search_biz_inst_topo(kwargs)
            return result
        except ComponentCallError as e:
            logger.error("esb->call search_biz_inst_topo error %s" % e.message)
            return []

    def cmdb_biz_free_inst_topo(self, biz):
        """
        搜索业务的空闲机池拓扑树
        :return:
        """

        kwargs = {"bk_biz_id": biz}
        try:
            # 需要以用户的名字进行请求
            result = client_v2.cc.get_biz_internal_module(kwargs)
            return result
        except ComponentCallError as e:
            logger.error("esb->call get_biz_internal_module error %s" % e.message)
            return {"info": []}

    def cmdb_hosts_by_biz(self, start, bk_biz_id, bk_set_ids=None, bk_module_ids=None):
        """
        Host列表
        :param start: 开始数
        :param bk_biz_id: 业务ID
        :param bk_set_id: 集群ID列表
        :param bk_module_ids: 模块ID列表
        :return: 主机列表
        """
        kwargs = {
            "page": {"start": start * 500, "limit": 500, "sort": "bk_host_id"},
            "bk_biz_id": bk_biz_id,
            "fields": ["bk_host_id"],
        }
        try:
            if bk_set_ids:
                kwargs["bk_set_ids"] = bk_set_ids
            if bk_module_ids:
                kwargs["bk_module_ids"] = bk_module_ids
            result = client_v2.cc.list_biz_hosts(kwargs)
            return result
        except ComponentCallError as e:
            logger.error("esb->call list_biz_hosts error %s" % e.message)
            return {"info": []}

    def fetch_host_ids_by_biz(self, bk_biz_id, bk_set_ids, bk_module_ids):
        """
        根据集群或者模块获得所有host id.
        :param inst: set or module
        :return: host_id 数组
        """

        host_info = self.cmdb_hosts_by_biz(0, bk_biz_id, bk_set_ids, bk_module_ids)

        def _fetch_host_data(result):
            bk_host_ids = []
            for instance in result["info"]:
                bk_host_ids.append(instance["bk_host_id"])
            return bk_host_ids

        count = host_info.get("count", 0)
        pages = int((count + 500 - 1) / 500)
        bk_host_ids = _fetch_host_data(host_info)

        if pages > 1:
            # 多页异步查询
            with ThreadPoolExecutor(max_workers=settings.CONCURRENT_NUMBER) as ex:
                tasks = [
                    ex.submit(self.cmdb_hosts_by_biz, page, bk_biz_id, bk_set_ids, bk_module_ids)
                    for page in range(1, pages)
                ]
                for future in as_completed(tasks):
                    host_info = future.result()
                    bk_host_ids.extend(_fetch_host_data(host_info))

        return bk_host_ids

    def cmdb_or_cache_topo(self, username: str, user_biz: dict, biz_host_id_map: dict):
        """
        如果有缓存，则返回缓存；
        如果没有缓存，则重新调取接口。
        :param username: 用户名
        :param user_biz:用户业务
        :param biz_host_id_map: 业务和相关Host ID字典
        格式:
        {
            'bk_host_id': ['蓝鲸/集群/模块', ...]
        }
        """

        user_page_topology_cache = cache.get(username + "_" + str(biz_host_id_map) + "_topo_cache")

        if user_page_topology_cache:
            # 如果存在缓存则返回
            return user_page_topology_cache
        else:
            # 缓存已过期，重新获取
            # 根据业务获得拓扑信息
            topology = {}
            # 异步需要用用户的名字，并且backend为True的形式请求
            with ThreadPoolExecutor(max_workers=settings.CONCURRENT_NUMBER) as ex:
                tasks = [
                    ex.submit(CmdbHandler().find_host_topo, username, biz, biz_host_id_map[biz], topology, user_biz)
                    for biz in biz_host_id_map
                ]
                as_completed(tasks)
            cache.set(username + "_" + str(biz_host_id_map) + "_topo_cache", topology, 300)
            return topology

    def biz(self, param):
        """
        查询用户所有业务
        格式:
        [{
            'bk_biz_id': biz_id ,
            'bk_biz_name': bk_biz_name
        }]
        """

        return self.ret_biz_permission(param)

    def biz_id_name(self, param):
        """
        获得用户的业务列表
        :return
        {
            bk_biz_id: bk_biz_name
        }
        """

        result = self.ret_biz_permission(param)

        return {biz["bk_biz_id"]: biz["bk_biz_name"] for biz in result}

    def cmdb_update_host(self, bk_host_id, properties):
        """
        更新host的属性
        :param bk_host_id: 需要修改的host的bk_host_id
        :param properties: 需要修改属性值
        :return: 返回查询结果
        """

        kwargs = {"update": [{"properties": properties, "bk_host_id": bk_host_id}]}
        # 增删改查CMDB操作以admin用户进行
        client_v2.cc.batch_update_host(kwargs)

    def cmdb_update_host_cloud(self, kwargs: dict):
        """
        更新host的云区域属性
        :param kwargs: 参数列表
        :return: None
        """

        # 增删改查CMDB操作以admin用户进行
        client_v2.cc.update_host_cloud_area_field(kwargs)

    def find_host_topo(self, username, bk_biz_id: int, bk_host_ids: list, topology: dict, user_biz: dict):
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "fields": ["bk_host_id"],
            "page": {"start": 0, "limit": len(bk_host_ids)},
            "host_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_host_id", "operator": "in", "value": bk_host_ids}],
            },
        }
        # 异步需要用用户的名字，并且backend为True的形式请求
        host_topos = client_v2.cc.list_biz_hosts_topo(kwargs, bk_username=username).get("info") or []
        for topos in host_topos:
            topology[topos["host"]["bk_host_id"]] = []
            # 集群
            for topo in topos["topo"]:
                topo_str = user_biz.get(bk_biz_id) + " / " + topo.get("bk_set_name")
                # 模块
                if topo.get("module", []):
                    for module in topo["module"]:
                        topology[topos["host"]["bk_host_id"]].append(topo_str + " / " + module["bk_module_name"])
        return topology

    @staticmethod
    def add_cloud(bk_cloud_name):
        """
        新增云区域
        """
        try:
            # 增删改查CMDB操作以admin用户进行
            data = client_v2.cc.create_cloud_area({"bk_cloud_name": bk_cloud_name})
            return data.get("created", {}).get("id")
        except ComponentCallError as e:
            if e.message and e.message["code"] == 1199048:
                raise CmdbAddCloudPermissionError(_("您没有增加CMDB云区域的权限"),)
            logger.error("esb->call create_cloud_area error %s" % e.message)
            data = client_v2.cc.create_inst({"bk_obj_id": "plat", "bk_cloud_name": bk_cloud_name})

            return data.get("bk_cloud_id")

    @staticmethod
    def delete_cloud(bk_cloud_id):
        """
        删除云区域
        """
        try:
            # 增删改查CMDB操作以admin用户进行
            return client_v2.cc.delete_cloud_area(
                {
                    # "bk_supplier_account": settings.DEFAULT_SUPPLIER_ACCOUNT,
                    "bk_cloud_id": bk_cloud_id
                }
            )
        except ComponentCallError as e:
            if e.message and e.message["code"] == 1101030:
                raise CloudUpdateAgentError(_("在CMDB中，还有主机关联到当前云区域下，无法删除"),)
            logger.error("esb->call delete_cloud_area error %s" % e.message)
            return client_v2.cc.delete_inst(
                {
                    "bk_supplier_account": settings.DEFAULT_SUPPLIER_ACCOUNT,
                    "bk_obj_id": "plat",
                    "bk_inst_id": bk_cloud_id,
                }
            )

    @staticmethod
    def get_cloud(bk_cloud_name):
        try:
            # 增删改查CMDB操作以admin用户进行
            plats = client_v2.cc.search_cloud_area({"condition": {"bk_cloud_name": bk_cloud_name}})
        except ComponentCallError as e:
            logger.error("esb->call search_cloud_area error %s" % e.message)
            plats = client_v2.cc.search_inst(
                {
                    "bk_obj_id": "plat",
                    "condition": {"plat": [{"field": "bk_cloud_name", "operator": "$eq", "value": bk_cloud_name}]},
                }
            )

        if plats["info"]:
            return plats["info"][0]["bk_cloud_id"]
        raise CloudNotExistError

    @staticmethod
    def rename_cloud(bk_cloud_id, bk_cloud_name):
        try:
            # 增删改查CMDB操作以admin用户进行
            client_v2.cc.update_cloud_area({"bk_cloud_id": bk_cloud_id, "bk_cloud_name": bk_cloud_name})
        except ComponentCallError as e:
            logger.error("esb->call update_cloud_area error %s" % e.message)
            client_v2.cc.update_inst(bk_obj_id="plat", bk_inst_id=bk_cloud_id, bk_cloud_name=bk_cloud_name)

    @classmethod
    def get_or_create_cloud(cls, bk_cloud_name):
        try:
            return cls.get_cloud(bk_cloud_name)
        except CloudNotExistError:
            return cls.add_cloud(bk_cloud_name)

    def fetch_topo(self, params: dict, username: str, is_superuser: bool):
        """
        获得相关业务数据的拓扑
        :param params: 参数列表
        :param username: 用户名
        :param is_superuser: 是否超管
        """

        def _recursion_get_child(inst):
            """
            递归求子结构
            :param inst: 实例
            """
            children = []
            if inst["child"]:
                for child in inst["child"]:
                    children.append(
                        {
                            "name": child["bk_inst_name"],
                            "id": child["bk_inst_id"],
                            "type": child["bk_obj_id"],
                            "children": _recursion_get_child(child),
                        }
                    )
            return children

        # 用户有权限获取的业务
        # 格式 { bk_biz_id: bk_biz_name , ...}
        user_biz = CmdbHandler().biz_id_name({"action": IamActionType.agent_view})
        bk_biz_id = params["bk_biz_id"]

        if not user_biz.get(bk_biz_id) and not is_superuser:
            raise BusinessNotPermissionError(_("您没有该业务权限"))

        result = cache.get(f"{username}_{bk_biz_id}_topo_cache")

        if result:
            # 如果存在缓存则返回
            return result
        else:
            result = []
            # 获取空闲机池和空闲机模块
            free_topos = CmdbHandler().cmdb_biz_free_inst_topo(bk_biz_id)
            free_modules = []
            if free_topos.get("module", []):
                modules = free_topos.get("module", [])
            else:
                modules = []
            for module in modules:
                free_modules.append(
                    {"id": module["bk_module_id"], "name": module["bk_module_name"], "type": "module", "children": []}
                )
            result.append(
                {
                    "name": free_topos.get("bk_set_name"),
                    "id": free_topos.get("bk_set_id"),
                    "type": "set",
                    "children": free_modules,
                }
            )

            # 获取业务拓扑树
            topos = CmdbHandler().cmdb_biz_inst_topo(bk_biz_id)
            if not topos:
                # 异常状态直接返回，不要缓存
                return result

            for child in topos[0]["child"]:
                result.append(
                    {
                        "name": child["bk_inst_name"],
                        "id": child["bk_inst_id"],
                        "type": child["bk_obj_id"],
                        "children": _recursion_get_child(child),
                    }
                )

            cache.set(f"{username}_{bk_biz_id}_topo_cache", result, 300)
        return result
