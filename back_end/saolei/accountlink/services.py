from datetime import datetime, timezone as datetime_timezone
import logging

from asgiref.sync import async_to_sync
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from django_tasks_db.models import DBTaskResult
import requests

from config.text_choices import MS_TextChoices, Saolei_TextChoices
from identifier.models import Identifier
from msuser.models import UserMS
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.parser import MSVideoParser
from utils.saolei import SaoleiUserInfo, SaoleiUtils
from videomanager.models import VideoModel
from .models import AccountMinesweeperGames, AccountSaolei, AccountWorldOfMinesweeper, Platform, VideoMSGames, VideoSaolei
from .msgames.client import download_replay as download_msgames_replay, fetch_profile as fetch_msgames_profile, fetch_replays as fetch_msgames_replays
from .msgames.utils import upload_date_upper_bound
from .utils import fetch_saolei_profile, fetch_saolei_video_download_and_state, update_bilibili_account
from .wom.client import fetch_wom_profile

logger = logging.getLogger('accountlink')

SAOLEI_VIDEO_IMPORT_TASK_PATH = 'accountlink.tasks.task_saolei_video_import'
SAOLEI_VIDEO_IMPORT_BULK_TASK_PATH = 'accountlink.tasks.task_saolei_video_import_bulk'


def update_account(platform: Platform, user: UserProfile):
    if platform == Platform.SAOLEI:
        update_saolei_account_info(user.account_saolei)
    elif platform == Platform.MSGAMES:
        update_msgames_account(user.account_msgames)
    elif platform == Platform.WOM:
        update_wom_account(user.account_wom)
    elif platform == Platform.BILIBILI:
        update_bilibili_account(user.account_bilibili)
    elif platform == Platform.MINERACER:
        raise ExceptionToResponse('mineracer', 'update_not_supported', status_code=400)


def update_wom_account(account: AccountWorldOfMinesweeper):
    data = async_to_sync(fetch_wom_profile)(account.id)
    for field, value in data.items():
        setattr(account, field, value)
    account.save(update_fields=[*data, 'update_time'])


def update_msgames_account(account: AccountMinesweeperGames):
    data = fetch_msgames_profile(account.id)
    for field, value in data.items():
        setattr(account, field, value)
    account.save(update_fields=[*data, 'update_time'])


def update_msgames_video_list(account: AccountMinesweeperGames) -> list[int]:
    data = fetch_msgames_replays(account.id)
    new_ids = []
    with transaction.atomic():
        account = AccountMinesweeperGames.objects.select_for_update().get(pk=account.pk)
        for info in data:
            key = info['source_key']
            defaults = {field: value for field, value in info.items() if field != 'source_key'}
            video, created = VideoMSGames.objects.update_or_create(user=account, source_key=key, defaults=defaults)
            if created:
                new_ids.append(video.id)
        account.video_update_time = timezone.now()
        account.save(update_fields=['video_update_time'])
    return new_ids


def msgames_video_import_one(source: VideoMSGames):
    if source.import_video_id:
        return source.import_video
    if not source.can_import:
        raise ExceptionToResponse('file', 'type', status_code=400)
    data = download_msgames_replay(source.url)
    filename = source.filename.rsplit('.', 1)[0] + '.' + source.filename.rsplit('.', 1)[1].lower()
    parser = MSVideoParser(ContentFile(data, filename))
    with transaction.atomic():
        source = VideoMSGames.objects.select_for_update().select_related('user__parent').get(pk=source.pk)
        if source.import_video_id:
            return source.import_video
        if not source.can_import:
            raise ExceptionToResponse('file', 'type', status_code=400)
        source_time = upload_date_upper_bound(source.upload_date) if source.upload_date else None
        for collision in VideoModel.objects.filter(file_size=len(data)).order_by('id'):
            try:
                with collision.file.open('rb') as file:
                    same_file = file.read() == data
            except OSError:
                continue
            if same_file:
                if source_time and collision.upload_time > source_time:
                    collision.upload_time = source_time
                    collision.save(update_fields=['upload_time'])
                source.import_video = collision
                source.save(update_fields=['import_video'])
                return collision
        user = source.user.parent
        if not user.userms_id:
            user.userms = UserMS.objects.create()
            user.save(update_fields=['userms'])
        if parser.state == MS_TextChoices.State.OFFICIAL and not Identifier.verify(parser.identifier, user.userms):
            parser.state = MS_TextChoices.State.IDENTIFIER
        video = VideoModel.create_from_parser(parser, user)
        if source_time:
            video.upload_time = source_time
        video.update_redis()
        video.save(update_fields=['upload_time', 'ongoing_tournament'])
        source.import_video = video
        source.save(update_fields=['import_video'])
        return video


def _get_task_identity(args: list, kwargs: dict, key: str):
    return kwargs.get(key, args[0] if args else None)


def restart_accountlink_task(db_task: DBTaskResult, args: list, kwargs: dict):
    if db_task.task_path == SAOLEI_VIDEO_IMPORT_TASK_PATH:
        return restart_saolei_video_import_task(db_task, args, kwargs)
    if db_task.task_path == SAOLEI_VIDEO_IMPORT_BULK_TASK_PATH:
        return restart_saolei_video_import_bulk_task(db_task, args, kwargs)
    return None


def restart_saolei_video_import_task(db_task: DBTaskResult, args: list, kwargs: dict):
    saolei_video_id = _get_task_identity(args, kwargs, 'video_id')
    if saolei_video_id is None:
        raise ExceptionToResponse('task_restart', 'invalid_args', status_code=400)

    current_reference = (
        VideoSaolei.objects
        .select_for_update()
        .filter(id=saolei_video_id, import_task_id=db_task.id)
        .first()
    )
    if current_reference is None:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)

    new_db_task = db_task.task.enqueue(*args, **kwargs).db_result
    updated_count = (
        VideoSaolei.objects
        .filter(id=saolei_video_id, import_task_id=db_task.id)
        .update(import_task_id=new_db_task.id)
    )
    if not updated_count:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)
    return new_db_task


def restart_saolei_video_import_bulk_task(db_task: DBTaskResult, args: list, kwargs: dict):
    saolei_account_id = _get_task_identity(args, kwargs, 'saolei_id')
    if saolei_account_id is None:
        raise ExceptionToResponse('task_restart', 'invalid_args', status_code=400)

    current_reference = (
        AccountSaolei.objects
        .select_for_update()
        .filter(id=saolei_account_id, video_import_task_id=db_task.id)
        .first()
    )
    if current_reference is None:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)

    new_db_task = db_task.task.enqueue(*args, **kwargs).db_result
    updated_count = (
        AccountSaolei.objects
        .filter(id=saolei_account_id, video_import_task_id=db_task.id)
        .update(video_import_task_id=new_db_task.id)
    )
    if not updated_count:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)
    return new_db_task


def update_saolei_account_info(account: AccountSaolei):
    try:
        profile = fetch_saolei_profile(account.id)
    except requests.exceptions.Timeout:  # 请求超时
        logger.error(f'雷网 用户#{account.id} 信息获取失败：请求超时')
        raise ExceptionToResponse(obj='import', category='timeout')
    except IndexError:  # 解析html时超出索引
        logger.error(f'雷网 用户#{account.id} 信息获取失败：解析错误')
        raise ExceptionToResponse(obj='import', category='indexerror')
    except requests.exceptions.RequestException:  # 其他请求异常
        raise ExceptionToResponse(obj='import', category='requestexception')

    account.name = profile['name']
    account.total_views = profile['total_views']

    account.b_t_ms = profile['timems']['b']
    account.i_t_ms = profile['timems']['i']
    account.e_t_ms = profile['timems']['e']
    account.s_t_ms = profile['timems']['s']

    account.b_b_cent = profile['bvs_cent']['b']
    account.i_b_cent = profile['bvs_cent']['i']
    account.e_b_cent = profile['bvs_cent']['e']
    account.s_b_cent = profile['bvs_cent']['s']

    account.beg_count = profile['count']['b']
    account.int_count = profile['count']['i']
    account.exp_count = profile['count']['e']

    account.update_time = datetime.now(tz=datetime_timezone.utc)

    account.save(update_fields=[
        'name', 'total_views',
        'b_t_ms', 'i_t_ms', 'e_t_ms', 's_t_ms',
        'b_b_cent', 'i_b_cent', 'e_b_cent', 's_b_cent',
        'beg_count', 'int_count', 'exp_count',
        'update_time',
    ])


# 扫描一页扫雷网用户录像，返回新录像列表
def update_saolei_user_video_one_page(account: AccountSaolei, page: int):
    logger.info(f'开始扫描扫雷网用户#{account.id}的第{page}页录像列表')
    saolei_user = SaoleiUserInfo(saolei_id=account.id)
    try:
        video_list = SaoleiUtils.get_video_list(saolei_user.videos_url(page=page))
    except requests.exceptions.ConnectionError:
        logger.error(f'扫雷网用户#{account.id}的第{page}页录像列表获取失败：连接失败')
        raise ExceptionToResponse(obj='import', category='connection')

    if not video_list:
        logger.warning(f'扫雷网用户#{account.id}的第{page}页录像列表为空')
        raise ExceptionToResponse(obj='saolei', category='page_empty')
    existing_video_ids = list(VideoSaolei.objects.filter(id__in=[info.id for info in video_list]).values_list('id', flat=True))

    new_video_list: list[VideoSaolei] = []
    for video_info in video_list:
        if video_info.id not in existing_video_ids:
            new_video = VideoSaolei.objects.create(id=video_info.id, user=account, upload_time=video_info.upload_time, level=video_info.level, bv=video_info.bv, timems=video_info.timems, nf=video_info.nf)
            new_video_list.append(new_video)

    logger.info(f'扫雷网用户#{account.id}的第{page}页扫描完成，共{len(video_list)}个录像，其中{len(new_video_list)}个新录像')
    return new_video_list


# 导入一个扫雷网录像
def saolei_video_import_one(saolei_video: VideoSaolei):
    logger.info(f'开始导入扫雷网录像#{saolei_video.id}')
    try:
        download_url, state = fetch_saolei_video_download_and_state(saolei_video.id)
        saolei_video.state = state
        saolei_video.save(update_fields=['state'])

        if state == Saolei_TextChoices.SaoleiVideoState.NOTEXIST:
            logger.warning(f'扫雷网 录像#{saolei_video.id} 不存在，可能已被删除')
            return

        file_name = download_url.split('/')[-1]

        response = requests.get(url=download_url, timeout=5)
        file_size = response.headers.get('Content-Length')
        if file_size is None:
            logger.error(f'雷网 录像#{saolei_video.id} 下载失败：无法获取文件大小')
            raise ExceptionToResponse(obj='import', category='unknown')

        collisions = VideoModel.objects.filter(file_size=file_size)
        for collision in collisions:
            if collision.file.read() == response.content:
                if collision.upload_time > saolei_video.upload_time:
                    collision.upload_time = saolei_video.upload_time
                    collision.save(update_fields=['upload_time'])
                saolei_video.import_video = collision
                saolei_video.save(update_fields=['import_video'])
                return

        parser = MSVideoParser(ContentFile(response.content, file_name))
        user = saolei_video.user.parent

        if not user.userms:
            user.userms = UserMS.objects.create()
        if not Identifier.verify(parser.identifier, user.userms) and parser.state == MS_TextChoices.State.OFFICIAL:
            parser.state = MS_TextChoices.State.IDENTIFIER

        video = VideoModel.create_from_parser(parser, user)
        video.upload_time = saolei_video.upload_time
        video.update_redis()
        video.save(update_fields=['upload_time', 'ongoing_tournament'])
        saolei_video.import_video = video
        saolei_video.save(update_fields=['import_video'])
    except requests.exceptions.ConnectionError:
        logger.error(f'雷网 录像#{saolei_video.id} 下载失败：连接错误')
        raise ExceptionToResponse(obj='import', category='connection')
    except requests.exceptions.ReadTimeout:
        logger.error(f'雷网 录像#{saolei_video.id} 下载失败：请求超时')
        raise ExceptionToResponse(obj='import', category='timeout')
    except BaseException as e:
        logger.error(f'雷网 录像#{saolei_video.id} 下载失败：未知错误')
        raise e
