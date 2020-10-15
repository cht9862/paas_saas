# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from collections import defaultdict
from copy import deepcopy
from hashlib import md5

import ujson as json
from django.core.cache import caches
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.backend.agent.tasks import collect_log
from apps.backend.agent.tools import gen_commands
from apps.backend.subscription.serializers import (
    CMDBSubscriptionSerializer,
    CreateSubscriptionSerializer,
    DeleteSubscriptionSerializer,
    FetchCommandsSerializer,
    GetSubscriptionSerializer,
    InstanceHostStatusSerializer,
    RetrySubscriptionSerializer,
    RevokeSubscriptionSerializer,
    RunSubscriptionSerializer,
    SwitchSubscriptionSerializer,
    TaskResultDetailSerializer,
    TaskResultSerializer,
    UpdateSubscriptionSerializer,
    RetryNodeSerializer,
)
from apps.backend.subscription.tasks import create_subscription_task, run_actions, run_subscription_task, retry_node
from apps.backend.subscription.tools import (
    create_group_id,
    create_node_id,
    get_instances_by_scope,
    get_subscription_task_instance_status,
)
from apps.backend.utils.pipeline_parser import PipelineParser
from apps.generic import APIViewSet
from apps.node_man import constants, models
from apps.node_man.models import Host, JobTask, SubscriptionTask
from pipeline.engine.models import PipelineProcess
from pipeline.service import task_service
from .errors import (
    ActionCanNotBeNone,
    SubscriptionInstanceRecordNotExist,
    SubscriptionNotExist,
    SubscriptionTaskNotExist,
)

logger = logging.getLogger("app")
cache = caches["db"]


class SubscriptionViewSet(APIViewSet):
    queryset = ""
    # permission_classes = (BackendBasePermission,)

    serializer_classes = dict(
        create_subscription=CreateSubscriptionSerializer,
        info=GetSubscriptionSerializer,
        update_subscription=UpdateSubscriptionSerializer,
        delete_subscription=DeleteSubscriptionSerializer,
        run=RunSubscriptionSerializer,
        revoke=RevokeSubscriptionSerializer,
        retry=RetrySubscriptionSerializer,
        task_result=TaskResultSerializer,
        switch=SwitchSubscriptionSerializer,
        cmdb_subscription=CMDBSubscriptionSerializer,
        fetch_commands=FetchCommandsSerializer,
        instance_status=InstanceHostStatusSerializer,
        task_result_detail=TaskResultDetailSerializer,
        retry_node=RetryNodeSerializer,
    )

    def get_validated_data(self):
        """
        使用serializer校验参数，并返回校验后参数
        :return: dict
        """
        data = None
        try:
            if self.request.method == "GET":
                data = self.request.query_params
            else:
                data = self.request.data
        except Exception as e:
            logger.info(e)

        try:
            if not data:
                data = json.loads(self.request.body)
        except Exception as e:
            raise ParseError(e)

        bk_username = self.request.META.get("HTTP_BK_USERNAME")
        bk_app_code = self.request.META.get("HTTP_BK_APP_CODE")

        data = data.copy()
        data.setdefault("bk_username", bk_username)
        data.setdefault("bk_app_code", bk_app_code)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return deepcopy(serializer.validated_data)

    def get_serializer_class(self):
        """
        根据方法名返回合适的序列化器
        """
        return self.serializer_classes.get(self.action)

    @action(detail=False, methods=["POST"], url_path="create")
    def create_subscription(self, request):
        """
        @api {POST} /subscription/create/ 创建订阅
        @apiName create_subscription
        @apiGroup subscription
        @apiParam {Object} scope 事件订阅监听的范围
        @apiParam {Int} scope.bk_biz_id 业务ID
        @apiParam {String} scope.object_type CMDB对象类型，可选 `SERVICE`, `HOST`
        @apiParam {String} scope.node_type CMDB节点类型，可选 `TOPO`, `INSTANCE`
        @apiParam {Object[]} scope.nodes 节点列表，根据 `object_type` 和 `node_type` 的不同，其数据结构也有所差异
        @apiParam {Object[]} steps 事件订阅触发的动作列表
        @apiParam {String} steps.id 步骤标识符，在一个列表中不允许重复
        @apiParam {String} steps.type 步骤类型，可选 `AGENT`, `PLUGIN`
        @apiParam {String} steps.config 步骤配置
        @apiParam {String} steps.params 步骤参数
        @apiParam {Object[]} [target_hosts] 需要下发的目标机器列表
        @apiParamExample {Json} 请求例子:
        {
            // 订阅节点，根据 object_type 和 node_type 的不同组合，数据结构有所差异
            "scope": {
                "bk_biz_id": 2,
                "object_type": "SERVICE",  // 可选 SERVICE - 服务，HOST - 主机
                "node_type": "TOPO",  // 可选 TOPO - 拓扑，INSTANCE - 实例
                "nodes": [
                    // SERVICE-INSTANCE
                    {
                       "id": 12
                    },
                    // HOST-TOPO
                    {
                        "bk_inst_id": 33,   // 节点实例ID
                        "bk_obj_id": "module",  // 节点对象ID
                    },
                    // HOST-INSTANCE
                    {
                        "ip": "10.0.0.1",
                        "bk_cloud_id": 0,
                        "bk_supplier_id": 0,
                    }
                ]
            },
            // 下发的目标机器，可以不传，默认取cmdb_instance.host下面的机器信息
            "target_hosts": [{
                "ip": "10.0.0.1",
                "bk_cloud_id": 0,
                "bk_supplier_id": 0
            }],
            "steps": [
                {
                    "id": "mysql_exporter",  // 步骤标识符，在一个列表中不允许重复
                    "type": "PLUGIN",   // 步骤类型
                    "config": {
                        "plugin_name": "mysql_exporter",
                        "plugin_version": "2.3",
                        "config_templates": [
                            {
                                "name": "config.yaml",
                                "version": "2",
                            },
                            {
                                "name": "env.yaml",
                                "version": "2",
                            }
                        ]
                    },
                    "params": {
                        "port_range": "9102,10000-10005,20103,30000-30100",
                        "context": {
                          // 输入常量
                          "--web.listen-host": "127.0.0.1",
                          // 使用 {{ }} 的方式引用节点管理内置变量
                          "--web.listen-port": "{{ control_info.port }}"
                        }
                    }
                },
                {
                    "id": "bkmonitorbeat",  // 步骤标识符，在一个列表中不允许重复
                    "type": "PLUGIN",   // 步骤类型
                    "config": {
                        "plugin_name": "bkmonitorbeat",
                        "plugin_version": "1.7.0",
                        "config_templates": [
                            {
                                "name": "bkmonitorbeat_exporter.yaml",
                                "version": "1",
                            },
                        ]
                    },
                    "params": {
                        "context": {
                            "metrics_url": "XXX",
                            // 以下为动态数组用法，用于渲染需要做循环的节点管理内置变量
                            "labels": {
                                "$for": "cmdb_instance.scopes",
                                "$item": "scope",
                                "$body": {
                                    "bk_target_ip": "{{ cmdb_instance.host.bk_host_innerip }}",
                                    "bk_target_cloud_id": "{{ cmdb_instance.host.bk_cloud_id }}",
                                    "bk_target_topo_level": "{{ scope.bk_obj_id }}",
                                    "bk_target_topo_id": "{{ scope.bk_inst_id }}",
                                    "bk_target_service_category_id": "{{ cmdb_instance.service.service_category_id }}",
                                    "bk_target_service_instance_id": "{{ cmdb_instance.service.id }}",
                                    "bk_collect_config_id": 1
                                }
                            }
                        }
                    }
                }
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "subscription_id": 1
            }
        }
        """
        params = self.get_validated_data()
        scope = params["scope"]
        run_immediately = params["run_immediately"]

        subscription_task = None

        with transaction.atomic():
            # 创建订阅
            subscription = models.Subscription.objects.create(
                bk_biz_id=scope["bk_biz_id"],
                object_type=scope["object_type"],
                node_type=scope["node_type"],
                nodes=scope["nodes"],
                target_hosts=params.get("target_hosts"),
                from_system="blueking",
                enable=False,
                is_main=params.get("is_main", False),
                creator=params["bk_username"],
            )

            # 创建订阅步骤
            steps = params["steps"]
            for index, step in enumerate(steps):
                models.SubscriptionStep.objects.create(
                    subscription_id=subscription.id,
                    index=index,
                    step_id=step["id"],
                    type=step["type"],
                    config=step["config"],
                    params=step["params"],
                )

            result = {
                "subscription_id": subscription.id,
            }

            if run_immediately:
                subscription_task = create_subscription_task(subscription)

        if subscription_task:
            run_subscription_task.delay(subscription_task)
            result["task_id"] = subscription_task.id

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="info")
    def info(self, request):
        """
        @api {POST} /subscription/info/ 订阅详情
        @apiName subscription_info
        @apiGroup subscription
        """
        params = self.get_validated_data()
        ids = params["subscription_id_list"]
        subscriptions = models.Subscription.get_subscriptions(ids)

        result = []
        for subscription in subscriptions:
            info = {
                "scope": {
                    "bk_biz_id": subscription.bk_biz_id,
                    "object_type": subscription.object_type,
                    "node_type": subscription.node_type,
                    "nodes": subscription.nodes,
                },
                "target_hosts": subscription.target_hosts,
                "steps": [],
            }

            for step in subscription.steps:
                info["steps"].append(
                    {"id": step.step_id, "type": step.type, "config": step.config, "params": step.params}
                )

            result.append(info)

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="update")
    def update_subscription(self, request):
        """
        @api {POST} /subscription/update/ 更新订阅
        @apiName update_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()
        scope = params["scope"]
        run_immediately = params["run_immediately"]
        subscription_task = None
        with transaction.atomic():
            try:
                subscription = models.Subscription.objects.get(id=params["subscription_id"], is_deleted=False)
            except models.Subscription.DoesNotExist:
                raise SubscriptionNotExist({"subscription_id": params["subscription_id"]})
            subscription.node_type = scope["node_type"]
            subscription.nodes = scope["nodes"]
            subscription.bk_biz_id = scope.get("bk_biz_id")
            subscription.save()

            steps_params = {step["id"]: step["params"] for step in params["steps"]}

            for step in subscription.steps:
                step.params = steps_params[step.step_id]
                step.save()

            result = {
                "subscription_id": subscription.id,
            }

            if run_immediately:
                subscription_task = create_subscription_task(subscription)

        # 如果是立即执行，则开始任务
        if subscription_task:
            run_subscription_task.delay(subscription_task)
            result["task_id"] = subscription_task.id

        return Response(result)

    @action(detail=False, methods=["POST"], url_path="delete")
    def delete_subscription(self, request):
        """
        @api {POST} /subscription/delete/ 删除订阅
        @apiName delete_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()
        try:
            subscription = models.Subscription.objects.get(id=params["subscription_id"], is_deleted=False)
        except models.Subscription.DoesNotExist:
            raise SubscriptionNotExist({"subscription_id": params["subscription_id"]})
        subscription.is_deleted = True
        subscription.save()
        return Response()

    @action(detail=False, methods=["POST"], url_path="run")
    def run(self, request):
        """
        @api {POST} /subscription/run/ 执行订阅
        @apiName run_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()
        actions = params.get("actions")
        scope = params.get("scope")

        try:
            subscription = models.Subscription.objects.get(id=params["subscription_id"], is_deleted=False)
        except models.Subscription.DoesNotExist:
            raise SubscriptionNotExist({"subscription_id": params["subscription_id"]})

        if not scope and not actions:
            # 如果不传范围和动作，则自动判断变更
            subscription_task = create_subscription_task(subscription)
        else:
            # 如果传了scope，那么必须有action
            if not actions:
                raise ActionCanNotBeNone()
            # 如果不传范围，则使用订阅全部范围
            if not scope:
                scope = subscription.scope
            else:
                scope["object_type"] = subscription.object_type
                scope["bk_biz_id"] = subscription.bk_biz_id
            subscription_task = run_actions(subscription, scope, actions)

        run_subscription_task.delay(subscription_task)

        return Response({"task_id": subscription_task.id})

    @action(detail=False, methods=["GET", "POST"], url_path="task_result")
    def task_result(self, request):
        """
        @api {POST} /subscription/task_result/ 任务执行结果
        @apiName subscription_task_result
        @apiGroup subscription
        """
        params = self.get_validated_data()
        subscription_id = params["subscription_id"]
        need_detail = params["need_detail"]

        try:
            subscription = models.Subscription.objects.get(id=subscription_id)
        except models.Subscription.DoesNotExist:
            raise SubscriptionNotExist({"subscription_id": subscription_id})

        if "task_id_list" in params:
            # 如果有task_id_list则查出订阅下的这些任务，新任务的instance记录会覆盖旧的
            task_id_list = set(params["task_id_list"])
            subscription_tasks = models.SubscriptionTask.objects.filter(
                id__in=task_id_list, subscription_id=subscription_id,
            )

            current_task_id_list = {task.id for task in subscription_tasks}
            if current_task_id_list != task_id_list:
                raise SubscriptionTaskNotExist({"task_id": list(task_id_list - current_task_id_list)})
        else:
            # 如果没传task_id则查询最近一次任务
            subscription_task = models.SubscriptionTask.objects.filter(subscription_id=subscription_id).first()
            task_id_list = [subscription_task.id]

        # 查询这些任务下的全部instance记录
        instance_records = models.SubscriptionInstanceRecord.objects.filter(task_id__in=task_id_list).order_by("id")

        # 实例去重
        instances_dict = {}
        for instance_record in instance_records:
            node_data = {
                "node_type": subscription.NodeType.INSTANCE,
                "object_type": subscription.object_type,
            }
            # 区分主机还是服务实例
            if subscription.object_type == subscription.ObjectType.HOST:
                host_info = instance_record.instance_info["host"]
                # 使用bk_host_id作业为会导致重试任务时无法去重
                node_data.update(
                    {
                        "ip": host_info["bk_host_innerip"],
                        "bk_cloud_id": host_info["bk_cloud_id"],
                        "bk_supplier_id": constants.DEFAULT_SUPPLIER_ID,
                    }
                )
            else:
                node_data.update({"id": instance_record.instance_info["service"]["id"]})
            node_id = create_node_id(node_data)
            instances_dict[node_id] = instance_record

        instance_records = list(instances_dict.values())

        pipeline_ids = [r.pipeline_id for r in instance_records]

        pipeline_parser = PipelineParser(pipeline_ids)

        instance_status = []
        for instance_record in instance_records:
            instance_status.append(get_subscription_task_instance_status(instance_record, pipeline_parser, need_detail))

        return Response(instance_status)

    @action(detail=False, methods=["GET", "POST"], url_path="task_result_detail")
    def task_result_detail(self, request):
        """
        @api {POST} /subscription/task_result_detail/ 任务执行详细结果
        @apiName subscription_task_result_detail
        @apiGroup subscription
        """
        params = self.get_validated_data()
        subscription_id = params["subscription_id"]
        task_id = params.get("task_id")
        instance_id = params["instance_id"]

        if not task_id:
            instance_record_qs = models.SubscriptionInstanceRecord.objects.filter(
                subscription_id=subscription_id, instance_id=instance_id
            )
            if not instance_record_qs.exists():
                raise SubscriptionInstanceRecordNotExist()
            instance_record = instance_record_qs.latest("create_time")
        else:
            instance_record = models.SubscriptionInstanceRecord.objects.filter(
                subscription_id=subscription_id, instance_id=instance_id, task_id=task_id,
            ).first()

        if not instance_record:
            raise SubscriptionInstanceRecordNotExist()

        pipeline_parser = PipelineParser([instance_record.pipeline_id])

        instance_status = get_subscription_task_instance_status(instance_record, pipeline_parser, need_detail=True)
        return Response(instance_status)

    @action(detail=False, methods=["POST"], url_path="collect_task_result_detail")
    def collect_task_result_detail(self, request):
        """
        @api {POST} /subscription/collect_task_result_detail/ 采集任务执行详细结果
        @apiName collect_subscription_task_result_detail
        @apiGroup subscription
        """
        job_id = self.request.data.get("job_id")
        instance_id = self.request.data.get("instance_id")
        try:
            job_task = JobTask.objects.get(job_id=job_id, instance_id=instance_id)
        except JobTask.DoesNotExist:
            return Response({"celery_id": -1})
        res = collect_log.delay(job_task.bk_host_id, job_task.pipeline_id)
        return Response({"celery_id": res.id})

    @action(detail=False, methods=["GET", "POST"], url_path="instance_status")
    def instance_status(self, request):
        """
        @api {POST} /subscription/instance_status/ 查询订阅运行状态
        @apiName query_instance_status
        @apiGroup subscription
        """
        params = self.get_validated_data()

        subscriptions = models.Subscription.objects.filter(id__in=params["subscription_id_list"], is_deleted=False)

        # 查出所有HostStatus
        instance_host_statuses = defaultdict(list)
        for host_status in models.ProcessStatus.objects.filter(
            source_id__in=params["subscription_id_list"], source_type=models.ProcessStatus.SourceType.SUBSCRIPTION,
        ):
            instance_host_statuses[host_status.group_id].append(host_status)

        # 查出所有InstanceRecord
        subscription_instance_record = defaultdict(dict)
        for instance_record in models.SubscriptionInstanceRecord.objects.filter(
            subscription_id__in=params["subscription_id_list"], is_latest=True,
        ):
            subscription_instance_record[instance_record.subscription_id][instance_record.instance_id] = instance_record

        node_ids = []

        # 获取所有实例的Pipeline节点ID
        for subscription_id in subscription_instance_record:
            records = subscription_instance_record[subscription_id]
            for instance_id in records:
                record = records[instance_id]
                if record.pipeline_id:
                    node_ids.append(record.pipeline_id)

        pipeline_parser = PipelineParser(node_ids)

        running_records = {}
        # 更新每条record的status字段
        for subscription_id in subscription_instance_record:
            records = subscription_instance_record[subscription_id]
            for instance_id in records:
                record = records[instance_id]
                # 注入 status 属性。查不到执行记录的，默认设为 PENDING
                record.status = pipeline_parser.get_node_state(record.pipeline_id)["status"]
                if record.status in ["PENDING", "RUNNING"]:
                    # 如果实例正在执行，则记下它对应的ID
                    running_records[record.task_id] = record

        # 查出正在运行实例对应的订阅任务，并建立record到task的映射关系
        subscription_tasks = models.SubscriptionTask.objects.filter(id__in=list(running_records.keys())).only(
            "id", "is_auto_trigger"
        )

        record_tasks = {}
        for task in subscription_tasks:
            record = running_records[task.id]
            record_tasks[record.id] = task

        result = []
        for subscription in subscriptions:
            subscription_result = []
            # 使用scope md5保证范围变化不会使用缓存
            m = md5()
            m.update(json.dumps(subscription.scope).encode())
            scope_md5 = m.hexdigest()
            current_instances = cache.get("bknodeman:subscription_scope_cache_{}".format(scope_md5), None)
            if current_instances is None:
                current_instances = get_instances_by_scope(subscription.scope)
                cache.set(
                    "bknodeman:subscription_scope_cache_{}".format(scope_md5), json.dumps(current_instances), 300,
                )
            else:
                current_instances = json.loads(current_instances)

            # 对于每个instance，通过group_id找到其对应的host_status
            for instance_id in current_instances:
                if instance_id in subscription_instance_record[subscription.id]:
                    instance_record = subscription_instance_record[subscription.id][instance_id]
                    group_id = create_group_id(subscription, instance_record.instance_info)

                    # 检查该实例是否有正在执行的任务
                    try:
                        related_task = record_tasks[instance_record.id]
                        running_task = {
                            "id": related_task.id,
                            "is_auto_trigger": related_task.is_auto_trigger,
                        }
                    except KeyError:
                        running_task = None

                    instance_result = {
                        "instance_id": instance_id,
                        "status": instance_record.status,
                        "create_time": instance_record.create_time,
                        "host_statuses": [],
                        "instance_info": instance_record.simple_instance_info(),
                        "running_task": running_task,
                        "last_task": {"id": instance_record.task_id},
                    }

                    if params["show_task_detail"]:
                        # 展示任务详情
                        instance_status = get_subscription_task_instance_status(
                            instance_record, pipeline_parser, need_detail=params.get("need_detail", False),
                        )
                        instance_status.pop("instance_info", None)
                        instance_status.pop("task_id", None)
                        instance_status.pop("instance_id", None)
                        instance_result["last_task"].update(instance_status)

                    for host_status in instance_host_statuses[group_id]:
                        instance_result["host_statuses"].append(
                            {"name": host_status.name, "status": host_status.status, "version": host_status.version}
                        )
                    subscription_result.append(instance_result)

            result.append({"subscription_id": subscription.id, "instances": subscription_result})
        return Response(result)

    @action(detail=False, methods=["POST"], url_path="switch")
    def switch(self, request):
        """
        @api {POST} /subscription/switch/ 订阅启停
        @apiName subscription_switch
        @apiGroup subscription
        """
        params = self.get_validated_data()
        try:
            subscription = models.Subscription.objects.get(id=params["subscription_id"], is_deleted=False)
        except models.Subscription.DoesNotExist:
            raise SubscriptionNotExist({"subscription_id": params["subscription_id"]})

        if params["action"] == "enable":
            subscription.enable = True
        elif params["action"] == "disable":
            subscription.enable = False

        subscription.save()

        return Response()

    @action(detail=False, methods=["POST"], url_path="revoke")
    def revoke(self, request):
        """
        @api {POST} /subscription/revoke/ 终止正在执行的任务
        @apiName revoke_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()
        instance_id_list = params.get("instance_id_list", [])
        subscription_id = params["subscription_id"]

        # 如果不传终止范围，则查询正在执行中的任务
        if not instance_id_list:
            instance_id_list = []
            instance_records = models.SubscriptionInstanceRecord.objects.filter(
                subscription_id=subscription_id, is_latest=True
            )
            pipeline_parser = PipelineParser([record.pipeline_id for record in instance_records])

            for instance_record in instance_records:
                instance_status = get_subscription_task_instance_status(instance_record, pipeline_parser)
                if instance_status["status"] in ["RUNNING", "PENDING"]:
                    instance_id_list.append(instance_record.instance_id)

        records = models.SubscriptionInstanceRecord.objects.filter(
            subscription_id=subscription_id, instance_id__in=instance_id_list
        )
        pipeline_ids = [r.pipeline_id for r in records]

        for process in PipelineProcess.objects.filter(root_pipeline_id__in=pipeline_ids):
            try:
                task_service.forced_fail(process.current_node_id)
            except Exception as error:
                logger.error(f"[forced_fail] failed with error: {error}")
                continue
        for pipeline_id in pipeline_ids:
            try:
                task_service.revoke_pipeline(pipeline_id)
            except Exception as error:
                logger.error(f"[revoke_pipeline] failed with error: {error}")
                continue
        return Response()

    @action(detail=False, methods=["POST"], url_path="retry")
    def retry(self, request):
        """
        @api {POST} /subscription/retry/ 重试失败的任务
        @apiName retry_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()
        instance_id_list = params.get("instance_id_list")
        subscription_id = params["subscription_id"]
        actions = params.get("actions")

        try:
            subscription = models.Subscription.objects.get(id=params["subscription_id"], is_deleted=False)
        except models.Subscription.DoesNotExist:
            raise SubscriptionNotExist({"subscription_id": params["subscription_id"]})

        # 如果不传终止范围，则查询已失败的任务
        if not instance_id_list:
            instance_id_list = []
            instance_records = models.SubscriptionInstanceRecord.objects.filter(
                subscription_id=subscription_id, is_latest=True
            )
            pipeline_parser = PipelineParser([record.pipeline_id for record in instance_records])

            for instance_record in instance_records:
                instance_status = get_subscription_task_instance_status(instance_record, pipeline_parser)
                if instance_status["status"] == "FAILED":
                    instance_id_list.append(instance_record.instance_id)

        scope = deepcopy(subscription.scope)
        scope["nodes"] = []
        for node in subscription.scope["nodes"]:
            _node = deepcopy(node)
            _node.update({"object_type": scope["object_type"], "node_type": scope["node_type"]})
            if create_node_id(_node) in instance_id_list:
                scope["nodes"].append(node)
        if not actions:
            # 如果没有传入actions，则以最近一次任务的action执行
            last_task = SubscriptionTask.objects.filter(subscription_id=subscription_id).order_by("create_time").first()
            try:
                # 这里认为一次订阅任务的action都是一致的
                actions = list(last_task.actions.values())[0]
            except Exception:
                raise SubscriptionTaskNotExist("无法自动获取最后一次执行的action，请尝试显式传入actions")
        subscription_task = run_actions(subscription, scope, actions)
        run_subscription_task.delay(subscription_task)
        return Response({"task_id": subscription_task.id})

    @action(detail=False, methods=["POST"], url_path="retry_node")
    def retry_node(self, request):
        """
        @api {POST} /subscription/retry_node/ 重试原子
        @apiName retry_node
        @apiGroup subscription
        @apiParam {String} instance_id 实例id
        @apiParam {Number} subscription_id 订阅id
        @apiParamExample {Json} 重试时请求参数
        {
            "instance_id": host|instance|host|20.7.18.2-0-0
            "subscription_id": 123
        }
        @apiSuccessExample {json} 成功返回:
        {
            "retry_node_id": "6f48169ed1193574961757a57d03a778",
            "retry_node_name": "安装"
        }
        """
        params = self.get_validated_data()
        subscription_id = params["subscription_id"]
        instance_id = params["instance_id"]

        instance_record_qs = models.SubscriptionInstanceRecord.objects.filter(
            subscription_id=subscription_id, instance_id=instance_id
        )
        if not instance_record_qs.exists():
            raise SubscriptionInstanceRecordNotExist()

        instance_record = instance_record_qs.latest("create_time")
        pipeline_parser = PipelineParser([instance_record.pipeline_id])
        instance_status = get_subscription_task_instance_status(instance_record, pipeline_parser, need_detail=True)

        if not (instance_status["steps"] and instance_status["steps"][0].get("target_hosts")):
            raise SubscriptionInstanceRecordNotExist()

        # 找出第一个失败的节点
        failed_node = next(
            (
                node
                for node in instance_status["steps"][0]["target_hosts"][0].get("sub_steps")
                if node["status"] == constants.JobStatusType.FAILED
            ),
            None,
        )
        # 无法获取失败任务节点的情况：失败任务重试中，安装任务已正常完成
        if not failed_node:
            raise SubscriptionInstanceRecordNotExist("无法获取失败任务节点")
        retry_node.delay(failed_node["pipeline_id"])
        return Response({"retry_node_id": failed_node["pipeline_id"], "retry_node_name": failed_node["node_name"]})

    @action(detail=False, methods=["GET", "POST"], url_path="cmdb_subscription")
    def cmdb_subscription(self, request):
        """
        @api {POST} /subscription/cmdb_subscription/ 接收cmdb事件回调
        @apiName cmdb_subscription
        @apiGroup subscription
        """
        params = self.get_validated_data()

        cmdb_events = []
        for data in params["data"]:
            cmdb_events.append(
                models.CmdbEventRecord(
                    event_type=params["event_type"],
                    action=params["action"],
                    obj_type=params["obj_type"],
                    cur_data=data["cur_data"],
                    pre_data=data["pre_data"],
                )
            )
        models.CmdbEventRecord.objects.bulk_create(cmdb_events)
        return Response("ok")

    @action(detail=False, methods=["POST"], url_path="fetch_commands")
    def fetch_commands(self, request):
        """
        @api {POST} /subscription/fetch_commands/ 返回安装命令
        @apiName fetch_commands
        @apiGroup subscription
        """

        params = self.get_validated_data()
        host = Host.objects.get(bk_host_id=params["bk_host_id"])
        __, win_commands, __, __, pre_commands, run_cmd = gen_commands(
            host, params["host_install_pipeline_id"], params["is_uninstall"], params["batch_install"],
        )

        return Response({"win_commands": win_commands, "pre_commands": pre_commands, "run_cmd": run_cmd})
