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
    page = 1
    while True:
        try:
            new_video_list_page = update_saolei_user_video_one_page(saolei_account, page)
        except ExceptionToResponse as e:
            if e.obj == 'saolei' and e.category == 'page_empty':
                break
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
