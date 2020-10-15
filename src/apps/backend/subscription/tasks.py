# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import traceback
from collections import OrderedDict, defaultdict

from celery.task import periodic_task
from django.db import transaction
from django.utils import timezone

from apps.backend.celery import app
from apps.backend.subscription.constants import SUBSCRIPTION_UPDATE_INTERVAL, SUBSCRIPTION_UPDATE_SLICE_SIZE
from apps.backend.subscription.errors import InstanceTaskIsRunning, PluginValidationError, SubscriptionInstanceEmpty
from apps.backend.subscription.steps import StepFactory
from apps.backend.subscription.steps.agent import InstallAgent, InstallProxy
from apps.backend.subscription.tools import (
    get_instances_by_scope,
    get_subscription_task_instance_status,
    parse_host_key,
    parse_node_id,
)
from apps.backend.utils.pipeline_parser import PipelineParser, check_running_records
from apps.node_man import constants
from apps.node_man.models import Job, PipelineTree, Subscription, SubscriptionInstanceRecord, SubscriptionTask
from pipeline import builder
from pipeline.service import task_service

logger = logging.getLogger("app")


def build_instance_task(record, step_actions, step_managers, target_hosts):
    """
    按实例执行任务
    :param SubscriptionInstanceRecord record: InstanceRecord
    :param step_actions: 步骤动作
    :param step_managers: list 步骤信息
    :param target_hosts: list 目标机器
    :return:
    """

    instance_start = builder.EmptyStartEvent()
    instance_end = builder.EmptyEndEvent()

    current_node = instance_start

    if target_hosts:
        for step_id in step_managers:
            if step_id not in step_actions:
                continue
            step_manager = step_managers[step_id]

            action_name = step_actions[step_manager.step_id]
            action_manager = step_manager.create_action(action_name, record)

            # 执行action&更新状态
            sub_processes = []
            for target_host in target_hosts:
                # 根据主机获取子流程
                sub_process = action_manager.execute(target_host)
                sub_processes.append(sub_process)

            # 根据主机数量，生成并行网关
            step_name = "[{}] {}".format(step_id, action_manager.ACTION_DESCRIPTION)

            step_start = builder.EmptyStartEvent()
            step_end = builder.EmptyEndEvent()

            pg = builder.ParallelGateway()
            cg = builder.ConvergeGateway()
            step_start.extend(pg).connect(*sub_processes).to(pg).converge(cg).extend(step_end)

            step_pipeline = builder.SubProcess(start=step_start, name=step_name)
            action_manager.set_pipeline_id(step_pipeline.id)
            current_node = current_node.extend(step_pipeline)

    current_node.extend(instance_end)

    return instance_start


def build_task(subscription_task, instances_action, instance_records):
    """
    批量执行实例的步骤的动作
    :param subscription_task: int
    :param instances_action: {
        "instance_id_xxx": {
            "step_id_x": "INSTALL",
            "step_id_y": "UNINSTALL,
        }
    }
    :param instance_records
    """

    subscription = subscription_task.subscription

    instance_records_dict = {record.instance_id: record for record in instance_records}

    step_managers = OrderedDict()
    step_data = []
    for step in subscription.steps:
        step_managers[step.step_id] = StepFactory.get_step_manager(step)
        step_data.append({"id": step.step_id, "type": step.type, "pipeline_id": "", "action": None, "extra_info": {}})

    to_be_saved_records = []
    to_be_saved_pipelines = []
    to_be_displayed_errors = []
    # 对每个实例执行指定动作
    for instance_id, step_actions in instances_action.items():
        record = instance_records_dict[instance_id]
        target_hosts = subscription.target_hosts

        # 如果没有指定目标机器，则取实例机器本身
        if not target_hosts:
            host_info = record.instance_info["host"]
            bk_cloud_id = host_info["bk_cloud_id"] or 0
            target_hosts = [
                {
                    "ip": host_info["bk_host_innerip"],
                    "bk_cloud_id": bk_cloud_id,
                    "bk_supplier_id": constants.DEFAULT_SUPPLIER_ID,
                }
            ]
        try:
            record.steps = step_data
            instance_task = build_instance_task(record, step_actions, step_managers, target_hosts)
        except PluginValidationError as err:
            # 插件操作系统不支持，忽略该实例
            logger.error(str(err))
            logger.error(traceback.format_exc())
            to_be_displayed_errors.append(str(err))
            continue

        # 构建 Pipeline 拓扑
        pipeline_tree = builder.build_tree(instance_task)
        pipeline_id = pipeline_tree["id"]
        record.pipeline_id = pipeline_id

        to_be_saved_records.append(record)
        to_be_saved_pipelines.append(PipelineTree(id=pipeline_id, tree=pipeline_tree,))

    return to_be_saved_records, to_be_saved_pipelines, to_be_displayed_errors


def create_task(subscription, instances, instance_actions, auto_trigger=False):
    """
    创建执行任务
    :param subscription: Subscription
    :param instances: dict
    :param instance_actions: {
        "instance_id_xxx": {
            "step_id_x": "INSTALL",
            "step_id_y": "UNINSTALL,
        }
    }
    :param auto_trigger: 是否为自动触发
    :return: SubscriptionTask
    """

    # 检查待运行实例中是否有正在运行的

    if check_running_records(
        SubscriptionInstanceRecord.objects.filter(
            subscription_id=subscription.id, instance_id__in=list(instance_actions.keys()), is_latest=True,
        )
    ):
        raise InstanceTaskIsRunning()

    with transaction.atomic():
        # 创建订阅任务记录
        subscription_task = SubscriptionTask.objects.create(
            subscription_id=subscription.id,
            scope=subscription.scope,
            actions=instance_actions,
            is_auto_trigger=auto_trigger,
        )

        # 批量创建订阅实例执行记录
        to_be_created_records = []
        for instance_id, action in instance_actions.items():
            # instance_id不在instances中，则说明该实例可能已经不在该业务中，因此无法操作，故不处理。
            if instance_id in instances:

                # 新装AGENT或PROXY会保存安装信息，需要清理
                if action.get("agent") in [
                    InstallAgent.ACTION_NAME,
                    InstallProxy.ACTION_NAME,
                ]:
                    need_clean = True
                else:
                    need_clean = False

                to_be_created_records.append(
                    SubscriptionInstanceRecord(
                        task_id=subscription_task.id,
                        subscription_id=subscription.id,
                        instance_id=instance_id,
                        instance_info=instances[instance_id],
                        steps=[],
                        is_latest=True,
                        need_clean=need_clean,
                    )
                )

        to_be_saved_records, to_be_saved_pipelines, to_be_displayed_errors = build_task(
            subscription_task, instance_actions, to_be_created_records
        )

        if auto_trigger:
            if not to_be_saved_records:
                # 如果是自动触发，且没有任何实例，那么直接抛出异常，回滚数据库
                raise SubscriptionInstanceEmpty()
        else:
            if not to_be_created_records:
                logger.error(",".join(to_be_displayed_errors) or "没有任何主机或配置没有任何变更")

        # 将最新属性重置
        SubscriptionInstanceRecord.objects.filter(
            subscription_id=subscription.id,
            is_latest=True,
            instance_id__in=[record.instance_id for record in to_be_saved_records],
        ).update(is_latest=False)
        SubscriptionInstanceRecord.objects.bulk_create(to_be_saved_records)
        PipelineTree.objects.bulk_create(to_be_saved_pipelines)

        logger.info("subscription({}) execute actions: {}".format(subscription.id, instance_actions))

    return subscription_task


def create_subscription_task(subscription, auto_trigger=False):
    """
    自动检查实例及配置的变更，执行相应动作
    :param subscription: Subscription
    :param auto_trigger: 是否为自动触发
    """

    # 获取订阅范围内全部实例
    instances = get_instances_by_scope(subscription.scope)
    logger.info(f"[create_subscription_task] instances={instances}")
    # 创建步骤管理器实例
    step_managers = {step.step_id: StepFactory.get_step_manager(step) for step in subscription.steps}

    # 按步骤顺序计算实例变更所需的动作
    instance_actions = defaultdict(dict)
    for step in step_managers.values():
        for instance_id, action in step.make_instances_migrate_actions(instances, auto_trigger=auto_trigger).items():
            instance_actions[instance_id][step.step_id] = action

    # 查询被从范围内移除的实例
    instance_not_in_scope = [instance_id for instance_id in instance_actions if instance_id not in instances]

    if instance_not_in_scope:
        deleted_id_not_in_scope = []
        for instance_id in instance_not_in_scope:
            if subscription.object_type == Subscription.ObjectType.HOST:
                host_key = parse_node_id(instance_id)["id"]
                deleted_id_not_in_scope.append(parse_host_key(host_key))
            else:
                service_instance_id = parse_node_id(instance_id)["id"]
                deleted_id_not_in_scope.append({"id": service_instance_id})

        deleted_instance_info = get_instances_by_scope(
            {
                "bk_biz_id": subscription.bk_biz_id,
                "object_type": subscription.object_type,
                "node_type": Subscription.NodeType.INSTANCE,
                "nodes": deleted_id_not_in_scope,
            }
        )

        # 如果被删掉的实例在 CMDB 找不到，那么就使用最近一次的 InstanceRecord 的快照数据
        not_exist_instance_id = set(instance_not_in_scope) - set(deleted_instance_info)

        if not_exist_instance_id:
            records = SubscriptionInstanceRecord.objects.filter(
                subscription_id=subscription.id, instance_id__in=not_exist_instance_id, is_latest=True,
            )
            for record in records:
                deleted_instance_info[record.instance_id] = record.instance_info

        instances.update(deleted_instance_info)

    return create_task(subscription, instances, instance_actions, auto_trigger)


def run_actions(subscription, scope, actions, auto_trigger=False):
    """
    执行指定动作
    :param subscription Subscription
    :param scope
    {
        "bk_biz_id": 2,
        "nodes": [],
        "node_type": "INSTANCE",
        "object_type": "HOST"
    }
    :param actions {
        "step_id_xxx": "INSTALL"
    }
    :param auto_trigger: 是否为自动触发任务
    """

    # 查询范围内的实例
    action_instances = get_instances_by_scope(scope)
    logger.info(f"[run_actions] action_instances={action_instances}")

    instance_actions = {instance_id: actions for instance_id in action_instances}
    subscription_task = create_task(subscription, action_instances, instance_actions, auto_trigger)

    return subscription_task


@app.task(queue="backend")
def run_subscription_task(subscription_task):
    pipeline_ids = {}
    for index, record in enumerate(subscription_task.instance_records):
        pipeline_ids[record.pipeline_id] = index

    from apps.node_man.models import PipelineTree

    pipelines = PipelineTree.objects.filter(id__in=list(pipeline_ids.keys()))
    ordered_pipelines = []
    for pipeline in pipelines:
        ordered_pipelines.append((pipeline_ids[pipeline.id], pipeline))
    # 排序
    ordered_pipelines.sort(key=lambda item: item[0])
    for index, pipeline in ordered_pipelines:
        pipeline.run(index % 255)


@app.task(queue="backend")
def retry_node(node_id):
    task_service.retry_activity(node_id)


@periodic_task(
    run_every=SUBSCRIPTION_UPDATE_INTERVAL,
    queue="backend",  # 这个是用来在代码调用中指定队列的，例如： update_subscription_instances.delay()
    options={"queue": "backend"},  # 这个是用来celery beat调度指定队列的
)
def update_subscription_instances():
    """
    定时触发订阅任务
    """
    subscription_ids = list(Subscription.objects.filter(enable=True, is_deleted=False).values_list("id", flat=True))

    for index in range(0, len(subscription_ids), SUBSCRIPTION_UPDATE_SLICE_SIZE):
        # 按照 SUBSCRIPTION_UPDATE_SLICE_SIZE 切分成多个分片
        chunks = subscription_ids[index : index + SUBSCRIPTION_UPDATE_SLICE_SIZE]
        update_subscription_instances_chunk.delay(chunks)


@app.task(queue="backend_additional_task")
def update_subscription_instances_chunk(subscription_ids):
    """
    分片更新订阅状态
    """
    subscriptions = Subscription.objects.filter(id__in=subscription_ids, enable=True, is_deleted=False)
    for subscription in subscriptions:

        try:
            if subscription.is_running():
                logger.info(
                    "[update_subscription_instances] subscription({subscription_id}) "
                    "task created failed, some instances is running".format(subscription_id=subscription.id)
                )
                continue

            subscription_task = create_subscription_task(subscription, auto_trigger=True)
            run_subscription_task.delay(subscription_task)
            logger.info(
                "[update_subscription_instances] subscription({subscription_id}) "
                "task created successful, task_id({task_id})".format(
                    subscription_id=subscription.id, task_id=subscription_task.id
                )
            )
        except SubscriptionInstanceEmpty:
            logger.info(
                "[update_subscription_instances] subscription({subscription_id}) "
                "has no change, do nothing.".format(subscription_id=subscription.id)
            )
        except Exception as e:
            logger.exception(
                "[update_subscription_instances] subscription({subscription_id}) task created failed, "
                "exception: {message}, {e}".format(subscription_id=subscription.id, message=traceback.format_exc(), e=e)
            )


@periodic_task(run_every=30, ignore_result=True)
def calculate_statistics():
    """
    统计未完成的任务中的主机信息
    """
    for job in Job.objects.filter(status=constants.JobStatusType.RUNNING):
        instance_records = SubscriptionInstanceRecord.objects.filter(
            subscription_id=job.subscription_id, is_latest=True
        ).order_by("id")
        # 去重
        instances_dict = {instance_record.instance_id: instance_record for instance_record in instance_records}
        instance_records = instances_dict.values()

        pipeline_ids = [r.pipeline_id for r in instance_records]

        pipeline_parser = PipelineParser(pipeline_ids)

        success_count = 0
        failed_count = 0
        running_count = 0
        pending_count = 0

        for instance_record in instance_records:
            status = get_subscription_task_instance_status(instance_record, pipeline_parser)["status"]

            if status == constants.JobStatusType.SUCCESS:
                success_count += 1
            elif status == constants.JobStatusType.FAILED:
                failed_count += 1
            elif status == constants.JobStatusType.RUNNING:
                running_count += 1
            else:
                pending_count += 1

        if running_count + pending_count == 0:
            # 所有IP都被执行完毕
            if failed_count == 0:
                job.status = constants.JobStatusType.SUCCESS
            elif success_count == 0:
                job.status = constants.JobStatusType.FAILED
            else:
                job.status = constants.JobStatusType.PART_FAILED
            job.end_time = timezone.now()

        job.statistics.update(
            {
                "success_count": success_count,
                "failed_count": failed_count,
                "running_count": running_count,
                "pending_count": pending_count,
            }
        )
        job.save(update_fields=["statistics", "status", "end_time"])
