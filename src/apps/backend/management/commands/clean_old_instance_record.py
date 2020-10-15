# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand

from apps.node_man.models import SubscriptionInstanceRecord, PipelineTree
from common.log import logger
from pipeline.engine.models import NodeRelationship, Status

STEP = 10000


def log_and_print(log):
    # 实时打屏显示进度
    logger.info("[clean_old_instance_record]{} {}".format(datetime.datetime.today(), log))
    print("[clean_old_instance_record]{} {}".format(datetime.datetime.today(), log))


def list_tree_node_ids(tree, node_ids=None):
    """根据pipeline tree递归得到所有节点id"""
    if node_ids is None:
        node_ids = []

    for flow_id, flow in tree.get("flows", {}).items():
        node_ids.append(flow_id)
        node_ids.append(flow["source"])
        node_ids.append(flow["target"])

    for activity_id, activity in tree.get("activities", {}).items():
        node_ids.append(activity_id)
        if "pipeline" in activity:
            list_tree_node_ids(activity["pipeline"], node_ids)


def clean_pipeline_data(index, pipeline_id, count, instance_record_pipeline_ids):
    """清理pipeline tree中无用的节点数据"""
    log_and_print("Cleaning {}/{} pipeline trees.".format(index + 1, count))
    if pipeline_id in instance_record_pipeline_ids:
        log_and_print("{} dose not need to clean, pass.".format(pipeline_id))
        return
    try:
        pipeline_tree = PipelineTree.objects.get(id=pipeline_id)
    except PipelineTree.DoesNotExist:
        log_and_print("{} dose not exist, pass.".format(pipeline_id))
        return
    node_ids = [pipeline_id]
    list_tree_node_ids(pipeline_tree.tree, node_ids)
    NodeRelationship.objects.filter(ancestor_id=pipeline_id).delete()
    Status.objects.filter(id__in=node_ids).delete()


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        清理老的instance record
        """
        start_time = time.time()
        # 由于部分环境的 SubscriptionInstanceRecord is_latest=True 的记录被删除
        # 这里通过pipeline_tree 查出无用的pipeline并清理相关数据
        pipeline_tree_ids = PipelineTree.objects.values_list("id", flat=True)
        instance_record_pipeline_ids = SubscriptionInstanceRecord.objects.filter(is_latest=True).values_list(
            "pipeline_id", flat=True
        )

        log_and_print("Counting pipeline trees.")
        count = pipeline_tree_ids.count()
        log_and_print("There are {} pipeline trees need to clean.".format(count))
        with ThreadPoolExecutor(max_workers=50) as ex:
            for index, pipeline_id in enumerate(pipeline_tree_ids.iterator(chunk_size=1)):
                ex.submit(clean_pipeline_data, index, pipeline_id, count, instance_record_pipeline_ids)

        log_and_print("total cost time: {}".format(time.time() - start_time))
