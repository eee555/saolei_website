from datetime import datetime, time

from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from ninja import Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from userprofile.decorators import login_required_error, staff_required
from .schema import CatalogItemOut, EnqueuedOut, GrantIdOut, GrantPageOut, PinsIn, PinsOut, PlayerMedalOut, RebuildIn, RevokeIn, StaffGrantIn
from .services import backfill_player, catalog_for, grant_manual, list_grants, MedalError, player_summary, refresh_player, replace_pins, revoke_manual
from .utils import GRANT_PAGE_SIZE, GRANT_PAGE_SIZE_MAX

router = Router()


def _http_error(exc: MedalError):
    if exc.code in {'user', 'definition', 'missing'}:
        raise HttpError(404, 'Not found')
    raise HttpError(400, 'Invalid medal request')


@router.get('/catalog', response=list[CatalogItemOut])
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_catalog(request):
    """
    - ratelimit(key='ip', rate='5/s')

    已启用的图鉴。未解锁的隐藏定义不出现。
    """
    return catalog_for(request.user)


@router.get('/players/{user_id}', response=PlayerMedalOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_medals(request, user_id: int):
    """
    - ratelimit(key='ip', rate='5/s')

    该玩家的勋章摘要、总分和佩戴。尚未做过历史扫描时只入队，不在这次请求里计算。
    """
    try:
        return player_summary(user_id)
    except MedalError as exc:
        _http_error(exc)


@router.get('/players/{user_id}/grants', response=GrantPageOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_grants(request, user_id: int, page: int = 1, page_size: int = GRANT_PAGE_SIZE):
    """
    - ratelimit(key='ip', rate='5/s')

    未撤销授予的分页。
    """
    page = max(1, page)
    page_size = min(max(1, page_size), GRANT_PAGE_SIZE_MAX)
    try:
        return list_grants(user_id, page, page_size)
    except MedalError as exc:
        _http_error(exc)


@router.put('/pins', response=PinsOut)
@decorate_view(login_required_error)
@decorate_view(ratelimit(key='user', rate='30/m', block=True))
def update_pins(request, payload: PinsIn):
    """
    - login_required_error
    - ratelimit(key='user', rate='30/m', block=True)

    替换本人的佩戴顺序，最多 6 个授予。
    """
    try:
        pin_ids = replace_pins(request.user, payload.grant_ids)
    except MedalError as exc:
        _http_error(exc)
    return {'pin_ids': pin_ids}


@router.post('/refresh', response=EnqueuedOut)
@decorate_view(login_required_error)
@decorate_view(ratelimit(key='user', rate='1/m', block=True))
def refresh_medals(request):
    """
    - login_required_error
    - ratelimit(key='user', rate='1/m', block=True)

    只入队当前用户的重算。
    """
    refresh_player(request.user.id)
    return {'enqueued': True}


@router.post('/staff/grants', response=GrantIdOut)
@decorate_view(staff_required)
def staff_grant(request, payload: StaffGrantIn):
    """
    - staff_required

    人工授予。纪念的具体规则在后续步骤。
    """
    granted_at = timezone.make_aware(datetime.combine(payload.granted_on, time.min), timezone.get_current_timezone())
    try:
        grant = grant_manual(request.user, payload.code, payload.user_id, payload.reason, granted_at)
    except MedalError as exc:
        _http_error(exc)
    return {'id': grant.id}


@router.post('/staff/grants/{grant_id}/revoke', response=GrantIdOut)
@decorate_view(staff_required)
def staff_revoke(request, grant_id: int, payload: RevokeIn):
    """
    - staff_required

    人工撤销，必须写原因。
    """
    try:
        grant = revoke_manual(grant_id, payload.reason)
    except MedalError as exc:
        _http_error(exc)
    return {'id': grant.id}


@router.post('/staff/rebuild', response=EnqueuedOut)
@decorate_view(staff_required)
def staff_rebuild(request, payload: RebuildIn):
    """
    - staff_required

    入队指定玩家的低优先级补发。请求里不重算。
    """
    try:
        backfill_player(payload.user_id)
    except MedalError as exc:
        _http_error(exc)
    return {'enqueued': True}
