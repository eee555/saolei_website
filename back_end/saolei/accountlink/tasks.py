from enum import Enum, auto
import requests

from django.tasks import task

from config.text_choices import Saolei_TextChoices
from videomanager.models import VideoModel

from .models import AccountSaolei, VideoSaolei
from .services import saolei_video_import_one, update_saolei_account_info, update_saolei_user_video_one_page
from .utils import update_saolei_account, fetch_saolei_video_download_and_state


@task
def task_saolei_video_import(video: VideoSaolei):
    saolei_video_import_one(video)


@task
def task_saolei_profile(saolei_account: AccountSaolei):
    update_saolei_account_info(saolei_account)


@task
def task_update_saolei_video_list(saolei_account: AccountSaolei, page: int):
    update_saolei_user_video_one_page(saolei_account, page)
