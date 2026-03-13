import logging

from django.tasks import task

from utils.exceptions import ExceptionToResponse

from .models import AccountSaolei, VideoSaolei
from .services import saolei_video_import_one, update_saolei_account_info, update_saolei_user_video_one_page

logger = logging.getLogger('accountlink')


@task(priority=-1)
def task_saolei_video_import(video_id: int):
    video = VideoSaolei.objects.get(id=video_id)
    saolei_video_import_one(video)


@task
def task_saolei_profile(saolei_id: int):
    saolei_account = AccountSaolei.objects.get(id=saolei_id)
    update_saolei_account_info(saolei_account)


@task
def task_update_saolei_video_list(saolei_id: int, mode: str):
    saolei_account = AccountSaolei.objects.get(id=saolei_id)

    # 重新导入失败的录像
    for saolei_video in saolei_account.videos.filter(import_video__isnull=True):
        if saolei_video.import_task:
            saolei_video.import_task.delete()
        saolei_video.import_task = task_saolei_video_import.enqueue(saolei_video.id).db_result
        saolei_video.save()

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
                    raise e
                connection_retry -= 1
                continue
            else:
                raise e

        if mode == 'new' and not new_video_list_page:
            break

        for video in new_video_list_page:
            import_task = video.import_task
            if not import_task:
                video.import_task = task_saolei_video_import.enqueue(video.id).db_result
                video.save()

        page += 1
