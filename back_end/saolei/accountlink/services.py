from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as datetime_timezone
import logging
from math import ceil
import secrets

from django.conf import settings
from django.core.cache import caches
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
from .mineracer import get_mineracer_account_link_poll_interval_ms, MINERACER_STATUS_CONFIRMED, MINERACER_STATUS_EXPIRED, MINERACER_STATUS_FAILED, MINERACER_STATUS_PENDING, poll_mineracer_account_link, request_mineracer_account_link
from .models import AccountLinkQueue, AccountMineracer, AccountSaolei, Platform, VideoSaolei
from .utils import fetch_saolei_profile, fetch_saolei_video_download_and_state, update_bilibili_account, update_msgames_account, update_wom_account

logger = logging.getLogger('accountlink')

SAOLEI_VIDEO_IMPORT_TASK_PATH = 'accountlink.tasks.task_saolei_video_import'
SAOLEI_VIDEO_IMPORT_BULK_TASK_PATH = 'accountlink.tasks.task_saolei_video_import_bulk'
MINERACER_USERID_LENGTHS = {9, 17}
MINERACER_CACHE_ALIAS = 'default'
MINERACER_SESSION_KEY_PREFIX = 'accountlink:mineracer:session'
MINERACER_USER_PENDING_KEY_PREFIX = 'accountlink:mineracer:user'
MINERACER_START_LOCK_SECONDS = 10
MINERACER_POLL_LOCK_SECONDS = 10
MINERACER_SESSION_ID_BYTES = 24
MINERACER_SESSION_GRACE_SECONDS = 60


@dataclass
class MineracerAccountLinkSession:
    id: str
    user_id: int
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_at: datetime
    status: str = MINERACER_STATUS_PENDING
    remote_userid: str = ''
    last_polled_at: datetime | None = None
    next_poll_at: datetime | None = None
    error_category: str = ''
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
        return None


def start_mineracer_account_link(user: UserProfile) -> MineracerAccountLinkSession:
    now = timezone.now()
    if _user_has_mineracer_link(user):
        logger.info('Mineracer link start rejected user_id=%s reason=already_linked', user.id)
        raise ExceptionToResponse('mineracer', 'already_linked', status_code=409)

    session = _get_pending_mineracer_session_for_user(user.id, now)
    if session:
        logger.info('Mineracer link start reused user_id=%s session_id=%s', user.id, session.id)
        return session

    lock_key = _mineracer_start_lock_key(user.id)
    cache = _mineracer_cache()
    if not cache.add(lock_key, '1', timeout=MINERACER_START_LOCK_SECONDS):
        session = _get_pending_mineracer_session_for_user(user.id, timezone.now())
        if session:
            logger.info('Mineracer link start reused user_id=%s session_id=%s reason=start_lock', user.id, session.id)
            return session
        logger.warning('Mineracer link start rejected user_id=%s reason=pending_start', user.id)
        raise ExceptionToResponse('mineracer', 'pending_start', status_code=409)

    try:
        session = _get_pending_mineracer_session_for_user(user.id, timezone.now())
        if session:
            logger.info('Mineracer link start reused user_id=%s session_id=%s reason=start_lock_recheck', user.id, session.id)
            return session

        remote_session = request_mineracer_account_link()
        now = timezone.now()
        if remote_session.expires_at <= now:
            logger.warning('Mineracer link start rejected user_id=%s reason=remote_expired', user.id)
            raise ExceptionToResponse('mineracer', 'expired')

        session = MineracerAccountLinkSession(
            id=_make_mineracer_session_id(),
            user_id=user.id,
            device_code=remote_session.device_code,
            user_code=remote_session.user_code,
            verification_uri=remote_session.verification_uri,
            verification_uri_complete=remote_session.verification_uri_complete,
            expires_at=remote_session.expires_at,
            next_poll_at=now + timedelta(milliseconds=remote_session.poll_interval_ms),
            created_at=now,
            updated_at=now,
        )
        _save_mineracer_session(session)
        _save_user_pending_mineracer_session(session)
        logger.info(
            'Mineracer link started user_id=%s session_id=%s expires_at=%s',
            user.id,
            session.id,
            session.expires_at.isoformat(),
        )
        return session
    finally:
        cache.delete(lock_key)


def poll_mineracer_account_link_session(user: UserProfile, session_id: str) -> MineracerAccountLinkSession | None:
    session = _get_owned_mineracer_session(user, session_id)
    if session is None:
        return None
    if session.status != MINERACER_STATUS_PENDING:
        return session

    now = timezone.now()
    if _is_mineracer_session_expired(session, now):
        return _mark_mineracer_session_expired(session)
    if session.next_poll_at and now < session.next_poll_at:
        return session

    lock_key = _mineracer_poll_lock_key(session.id)
    cache = _mineracer_cache()
    if not cache.add(lock_key, '1', timeout=MINERACER_POLL_LOCK_SECONDS):
        return _get_owned_mineracer_session(user, session.id) or session

    try:
        session = _prepare_mineracer_poll(user, session.id)
        if session is None or session.status != MINERACER_STATUS_PENDING:
            return session
        if session.next_poll_at and timezone.now() < session.next_poll_at:
            return session

        session.last_polled_at = timezone.now()
        session.next_poll_at = session.last_polled_at + timedelta(milliseconds=get_mineracer_account_link_poll_interval_ms())
        session.error_category = ''
        _save_mineracer_session(session)
        logger.info('Mineracer link poll sent user_id=%s session_id=%s', user.id, session.id)
        poll_result = poll_mineracer_account_link(session.device_code)
        if poll_result.status == MINERACER_STATUS_PENDING:
            return _update_pending_mineracer_session(session, poll_result.retry_after_ms)
        if poll_result.status == MINERACER_STATUS_CONFIRMED:
            return complete_mineracer_account_link(user, session, poll_result.userid)
        if poll_result.status == MINERACER_STATUS_EXPIRED:
            return _mark_mineracer_session_expired(session)
        if poll_result.status == MINERACER_STATUS_FAILED:
            return _mark_mineracer_session_failed(session, poll_result.error_category or 'remote_failed')
        raise ExceptionToResponse('mineracer', 'response')
    except ExceptionToResponse as exc:
        if exc.category in ['requestexception', 'timeout']:
            return _mark_mineracer_session_poll_error(session, exc.category)
        logger.warning('Mineracer link poll failed user_id=%s session_id=%s category=%s', user.id, session.id, exc.category)
        raise
    finally:
        cache.delete(lock_key)


def get_mineracer_session_retry_after_ms(session: MineracerAccountLinkSession) -> int:
    if session.status != MINERACER_STATUS_PENDING or session.next_poll_at is None:
        return 0
    return max(0, ceil((session.next_poll_at - timezone.now()).total_seconds() * 1000))


def complete_mineracer_account_link(user: UserProfile, session: MineracerAccountLinkSession, userid: str) -> MineracerAccountLinkSession | None:
    userid = str(userid).strip()
    if not _is_valid_mineracer_userid(userid):
        return _mark_mineracer_session_failed(session, 'invalid_userid', remote_userid=userid)
    if _is_mineracer_session_expired(session, timezone.now()):
        return _mark_mineracer_session_expired(session)

    identifier_conflict = False
    with transaction.atomic():
        collision = AccountLinkQueue.objects.select_for_update().filter(
            platform=Platform.MINERACER,
            identifier=userid,
            verified=True,
        ).exclude(userprofile=user).first()
        account_collision = AccountMineracer.objects.select_for_update().filter(id=userid).exclude(parent=user).first()
        existing_user_account = AccountMineracer.objects.select_for_update().filter(parent=user).exclude(id=userid).first()
        if collision or account_collision or existing_user_account:
            identifier_conflict = True
        else:
            AccountMineracer.objects.update_or_create(id=userid, defaults={'parent': user})
            AccountLinkQueue.objects.update_or_create(
                platform=Platform.MINERACER,
                userprofile=user,
                defaults={'identifier': userid, 'verified': True},
            )

    if identifier_conflict:
        _mark_mineracer_session_failed(session, 'identifier_conflict', remote_userid=userid)
        raise ExceptionToResponse('mineracer', 'identifier_conflict', status_code=409)
    return _mark_mineracer_session_confirmed(session, userid)


def _prepare_mineracer_poll(user: UserProfile, session_id: str) -> MineracerAccountLinkSession | None:
    session = _get_owned_mineracer_session(user, session_id)
    if session is None:
        return None
    if session.status != MINERACER_STATUS_PENDING:
        return session
    if _is_mineracer_session_expired(session, timezone.now()):
        return _mark_mineracer_session_expired(session)
    return session


def _update_pending_mineracer_session(session: MineracerAccountLinkSession, retry_after_ms: int | None = None) -> MineracerAccountLinkSession:
    if session.status == MINERACER_STATUS_PENDING and retry_after_ms is not None:
        session.next_poll_at = timezone.now() + timedelta(milliseconds=retry_after_ms)
    session.error_category = ''
    _save_mineracer_session(session)
    _save_user_pending_mineracer_session(session)
    logger.info('Mineracer link poll pending user_id=%s session_id=%s retry_after_ms=%s', session.user_id, session.id, get_mineracer_session_retry_after_ms(session))
    return session


def _mark_mineracer_session_poll_error(session: MineracerAccountLinkSession, category: str) -> MineracerAccountLinkSession:
    if session.status == MINERACER_STATUS_PENDING:
        session.error_category = category
        session.next_poll_at = timezone.now() + timedelta(milliseconds=get_mineracer_account_link_poll_interval_ms())
        _save_mineracer_session(session)
        _save_user_pending_mineracer_session(session)
    logger.warning('Mineracer link poll transient_error user_id=%s session_id=%s category=%s', session.user_id, session.id, category)
    return session


def _mark_mineracer_session_confirmed(session: MineracerAccountLinkSession, userid: str) -> MineracerAccountLinkSession:
    session.status = MINERACER_STATUS_CONFIRMED
    session.remote_userid = userid
    session.error_category = ''
    _delete_user_pending_mineracer_session(session.user_id)
    _save_mineracer_session(session, timeout=_get_mineracer_session_grace_seconds())
    logger.info('Mineracer link confirmed user_id=%s session_id=%s mineracer_userid=%s', session.user_id, session.id, userid)
    return session


def _mark_mineracer_session_expired(session: MineracerAccountLinkSession) -> MineracerAccountLinkSession:
    if session.status == MINERACER_STATUS_PENDING:
        session.status = MINERACER_STATUS_EXPIRED
    _delete_user_pending_mineracer_session(session.user_id)
    _save_mineracer_session(session, timeout=_get_mineracer_session_grace_seconds())
    logger.info('Mineracer link expired user_id=%s session_id=%s', session.user_id, session.id)
    return session


def _mark_mineracer_session_failed(session: MineracerAccountLinkSession, category: str, remote_userid: str = '') -> MineracerAccountLinkSession:
    if session.status == MINERACER_STATUS_PENDING:
        session.status = MINERACER_STATUS_FAILED
    session.error_category = category
    session.remote_userid = remote_userid
    _delete_user_pending_mineracer_session(session.user_id)
    _save_mineracer_session(session, timeout=_get_mineracer_session_grace_seconds())
    logger.warning('Mineracer link failed user_id=%s session_id=%s category=%s mineracer_userid=%s', session.user_id, session.id, category, remote_userid)
    return session


def _get_pending_mineracer_session_for_user(user_id: int, now: datetime) -> MineracerAccountLinkSession | None:
    session_id = _mineracer_cache().get(_mineracer_user_pending_key(user_id))
    if not session_id:
        return None
    session = _get_mineracer_session(str(session_id))
    if session is None or session.user_id != user_id:
        _delete_user_pending_mineracer_session(user_id)
        return None
    if session.status != MINERACER_STATUS_PENDING:
        _delete_user_pending_mineracer_session(user_id)
        return None
    if _is_mineracer_session_expired(session, now):
        _mark_mineracer_session_expired(session)
        return None
    return session


def _get_owned_mineracer_session(user: UserProfile, session_id: str) -> MineracerAccountLinkSession | None:
    session = _get_mineracer_session(session_id)
    if session is None or session.user_id != user.id:
        return None
    return session


def _get_mineracer_session(session_id: str) -> MineracerAccountLinkSession | None:
    value = _mineracer_cache().get(_mineracer_session_key(session_id))
    if not isinstance(value, MineracerAccountLinkSession):
        return None
    return value


def _save_mineracer_session(session: MineracerAccountLinkSession, timeout: int | None = None) -> MineracerAccountLinkSession:
    now = timezone.now()
    if session.created_at is None:
        session.created_at = now
    session.updated_at = now
    _mineracer_cache().set(
        _mineracer_session_key(session.id),
        session,
        timeout=timeout if timeout is not None else _get_mineracer_session_timeout_seconds(session, now),
    )
    return session


def _save_user_pending_mineracer_session(session: MineracerAccountLinkSession):
    if session.status != MINERACER_STATUS_PENDING:
        return
    _mineracer_cache().set(
        _mineracer_user_pending_key(session.user_id),
        session.id,
        timeout=_get_mineracer_user_pending_timeout_seconds(session, timezone.now()),
    )


def _delete_user_pending_mineracer_session(user_id: int):
    _mineracer_cache().delete(_mineracer_user_pending_key(user_id))


def _mineracer_cache():
    return caches[MINERACER_CACHE_ALIAS]


def _mineracer_session_key(session_id: str) -> str:
    return f'{MINERACER_SESSION_KEY_PREFIX}:{session_id}'


def _mineracer_user_pending_key(user_id: int) -> str:
    return f'{MINERACER_USER_PENDING_KEY_PREFIX}:{user_id}:pending'


def _mineracer_start_lock_key(user_id: int) -> str:
    return f'{MINERACER_USER_PENDING_KEY_PREFIX}:{user_id}:start_lock'


def _mineracer_poll_lock_key(session_id: str) -> str:
    return f'{MINERACER_SESSION_KEY_PREFIX}:{session_id}:poll_lock'


def _make_mineracer_session_id() -> str:
    cache = _mineracer_cache()
    for _ in range(3):
        session_id = secrets.token_urlsafe(MINERACER_SESSION_ID_BYTES)
        if cache.get(_mineracer_session_key(session_id)) is None:
            return session_id
    return secrets.token_urlsafe(MINERACER_SESSION_ID_BYTES)


def _get_mineracer_session_timeout_seconds(session: MineracerAccountLinkSession, now: datetime) -> int:
    seconds_to_expiry = (session.expires_at - now).total_seconds()
    return max(1, ceil(seconds_to_expiry + _get_mineracer_session_grace_seconds()))


def _get_mineracer_user_pending_timeout_seconds(session: MineracerAccountLinkSession, now: datetime) -> int:
    return max(1, ceil((session.expires_at - now).total_seconds()))


def _get_mineracer_session_grace_seconds() -> int:
    config = getattr(settings, 'MINERACER_ACCOUNT_LINK', {})
    return max(1, int(config.get('SESSION_GRACE_SECONDS', MINERACER_SESSION_GRACE_SECONDS)))


def _is_mineracer_session_expired(session: MineracerAccountLinkSession, now: datetime) -> bool:
    return now >= session.expires_at


def _user_has_mineracer_link(user: UserProfile) -> bool:
    return (
        AccountLinkQueue.objects.filter(platform=Platform.MINERACER, userprofile=user).exists()
        or AccountMineracer.objects.filter(parent=user).exists()
    )


def _is_valid_mineracer_userid(userid: str) -> bool:
    return len(userid) in MINERACER_USERID_LENGTHS


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
