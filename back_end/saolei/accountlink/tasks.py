from django.tasks import task

from utils.exceptions import ExceptionToResponse

from .models import AccountSaolei, VideoSaolei
from .services import saolei_video_import_one, update_saolei_account_info, update_saolei_user_video_one_page


@task
def task_saolei_video_import(video: VideoSaolei):
    saolei_video_import_one(video)


@task
def task_saolei_profile(saolei_account: AccountSaolei):
    update_saolei_account_info(saolei_account)


@task
def task_update_saolei_video_list(saolei_account: AccountSaolei, mode: str):
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
            video.import_task = task_saolei_video_import.enqueue(video)
            video.save()

        page += 1
