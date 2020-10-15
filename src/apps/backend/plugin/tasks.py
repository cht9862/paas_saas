# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import logging
import traceback

from apps.backend.celery import app
from apps.backend.utils.pipeline_parser import PipelineParser as CustomPipelineParser
from apps.node_man import constants as const
from apps.node_man import models
from pipeline.service import task_service

logger = logging.getLogger("app")


# 注意，这里强行写入了queue为backend，因为发现settings中的CELERY_ROUTES失效
# 有哪位大锅有好的想法的话，可以考虑减少这个配置
@app.task(queue="backend")
def package_task(job_id, task_params):
    """
    执行一个指定的打包任务
    :param job_id: job ID
    :param task_params: 任务参数
    :return:
    """
    # 1. 判断任务是否存在 以及 任务类型是否符合预期
    try:
        job = models.Job.objects.get(id=job_id, job_type=const.JobType.PACKING_PLUGIN)

    except models.Job.DoesNotExist:
        logger.error("try to execute job->[%s] but is not exists")
        return False

    try:
        file_name = task_params["file_name"]
        is_release = task_params["is_release"]
        # 使用最后的一条上传记录
        upload_package_object = models.UploadPackage.objects.filter(file_name=file_name).order_by("-upload_time")[0]

        # 2. 执行任务
        upload_package_object.create_package_records(is_release)

    except (ValueError, KeyError):
        logger.error("failed to get task->[{}] file_name for->[{}]".format(job_id, traceback.format_exc()))
        job.status = const.JobStatusType.FAILED
        job.save()
        return False

    except models.UploadPackage.DoesNotExist:
        logger.error("failed to get upload_package for job->[%s], task will not execute." % job_id)
        job.status = const.JobStatusType.FAILED
        job.save()
        # models.TaskLog.objects.create(
        #     level=const.LevelType.error,
        #     content="task params error, no such file upload record",
        #     job_id=job.id
        # )
        return False

    except Exception:
        logger.error("failed to finish task->[{}] for->[{}]".format(job_id, traceback.format_exc()))
        job.status = const.JobStatusType.FAILED
        job.save()

    finally:
        # 3. 更新任务状态
        job.status = const.JobStatusType.SUCCESS
        job.end_time = datetime.datetime.now()
        job.save()

        logger.info("task->[%s] has finish all job." % job.id)


@app.task(queue="backend")
def export_plugin(job_id):
    """
    开始导出一个插件
    :param job_id: 任务ID
    :return:
    """

    try:
        record = models.DownloadRecord.objects.get(id=job_id)
    except models.DownloadRecord.DoesNotExist:
        logger.error("record->[%s] not exists, nothing will do" % job_id)
        return

    record.execute()
    logger.info("record->[%s] execute success." % job_id)
    return


@app.task(queue="backend")
def run_pipeline(pipeline):
    task_service.run_pipeline(pipeline)


@app.task(queue="backend")
def stop_pipeline(pipeline_id, node_id):
    result = True
    message = "success"
    pipeline_parser = CustomPipelineParser([pipeline_id])
    state = pipeline_parser.get_node_state(node_id)["status"]
    if state == "RUNNING":
        # 正在调试的，直接强制终止
        task_service.forced_fail(node_id, ex_data="用户终止调试进程")
        operate_result = task_service.skip_activity(node_id)
        result = operate_result.result
        message = operate_result.message
    elif state == "PENDING":
        # 没在调试的，撤销任务
        operate_result = task_service.revoke_pipeline(pipeline_id)
        result = operate_result.result
        message = operate_result.message
    return result, message
