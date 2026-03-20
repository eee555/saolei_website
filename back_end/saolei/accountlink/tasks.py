import logging
from typing import Literal

from django.tasks import task
from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult

from utils.exceptions import ExceptionToResponse

from .models import AccountSaolei, VideoSaolei
from .services import saolei_video_import_one, update_saolei_account_info, update_saolei_user_video_one_page

logger = logging.getLogger('accountlink')


# 接口，请用这些创建任务

def helper_saolei_video_import_bulk(saolei_account: AccountSaolei, mode: Literal['all', 'new']):
    existing_task = saolei_account.video_import_task
    if existing_task:
        if existing_task.status == TaskResultStatus.SUCCESSFUL:
            existing_task.delete()
        elif existing_task.status == TaskResultStatus.FAILED:
            pass
        elif existing_task.status == TaskResultStatus.READY:
            return
        else:  # RUNNING
            return

    # 先清理旧的任务
    finished_saolei_videos = VideoSaolei.objects.filter(
        user=saolei_account,
        import_video__isnull=False,
        import_task__isnull=False
    ).values_list('import_task__id', flat=True)
    DBTaskResult.objects.filter(id__in=finished_saolei_videos).delete()

    saolei_account.video_import_task = task_saolei_video_import_bulk.enqueue(saolei_account.id, mode).db_result
    saolei_account.save(update_fields=['video_import_task'])


def helper_saolei_video_import(video_saolei: VideoSaolei):
    existing_task = video_saolei.import_task
    if existing_task:
        if existing_task.status == TaskResultStatus.SUCCESSFUL:
            existing_task.delete()
        elif existing_task.status == TaskResultStatus.FAILED:
            pass
        elif existing_task.status == TaskResultStatus.READY:
            return
        else:  # RUNNING
            return

    video_saolei.import_task = task_saolei_video_import.enqueue(video_saolei.id).db_result
    video_saolei.save(update_fields=['import_task'])


# 任务后端

@task(priority=-1)
def task_saolei_video_import(video_id: int):
    video = VideoSaolei.objects.get(id=video_id)
    connection_retry = 3
    while connection_retry > 0:
        try:
            saolei_video_import_one(video)
        except ExceptionToResponse as e:
            if e.obj == 'import' and e.category == 'connection':
                connection_retry -= 1
                continue
            elif e.obj == 'import' and e.category == 'timeout':
                connection_retry -= 1
                continue
            else:
                return e


@task
def task_saolei_profile(saolei_id: int):
    saolei_account = AccountSaolei.objects.get(id=saolei_id)
    update_saolei_account_info(saolei_account)


@task(priority=2)
def task_saolei_video_import_bulk(saolei_id: int, mode: str):
    # mode = 'all': 扫描所有页面
    # mode = 'new': 扫描到没有新录像为止

    saolei_account = AccountSaolei.objects.get(id=saolei_id)

    page = 1
    connection_retry = 3
    while True:
        try:
            new_video_list_page = update_saolei_user_video_one_page(saolei_account, page)
        except ExceptionToResponse as e:
            if e.obj == 'saolei' and e.category == 'page_empty':
                break
            elif e.obj == 'import' and e.category == 'connection':
                if connection_retry <= 0:
                    return e
                connection_retry -= 1
                continue
            else:
                raise e

        if mode == 'new' and len(new_video_list_page) < 22:
            break

        page += 1
        connection_retry = 3

    # 导入需要导入的录像
    saolei_video_list = VideoSaolei.objects.filter(user=saolei_account, import_video__isnull=True)
    for video in saolei_video_list:
        helper_saolei_video_import(video)
