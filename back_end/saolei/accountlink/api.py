from datetime import datetime
from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from utils.response import HttpResponseConflict
from .models import AccountBilibili, AccountLinkQueue, AccountMineracer, AccountMinesweeperGames, AccountQQ, AccountSaolei, AccountWorldOfMinesweeper, MineracerAccountLinkSession, Platform, PLATFORM_CONFIG
from .services import get_mineracer_session_retry_after_ms, poll_mineracer_account_link_session, start_mineracer_account_link
from .utils import private_platforms

router = Router()


AccountLinkOut = create_schema(
    AccountLinkQueue,
    fields=[
        'id', 'platform',
        'identifier', 'userprofile',
        'verified',
    ],
)


AccountLinkQueueOut = create_schema(AccountLinkQueue)
AccountSaoleiOut = create_schema(AccountSaolei)
AccountMSGamesOut = create_schema(AccountMinesweeperGames)
AccountWoMOut = create_schema(AccountWorldOfMinesweeper)
AccountBiliOut = create_schema(AccountBilibili)
AccountMineracerOut = create_schema(AccountMineracer)
AccountQQOut = create_schema(AccountQQ)


class AccountLinkCompleteOut(Schema):
    summary: list[AccountLinkQueueOut]
    B: AccountBiliOut | None = None
    c: AccountSaoleiOut | None = None
    a: AccountMSGamesOut | None = None
    m: AccountMineracerOut | None = None
    w: AccountWoMOut | None = None
    q: AccountQQOut | None = None


class AccountLinkCreateIn(Schema):
    platform: str
    identifier: str


class MineracerAccountLinkSessionOut(Schema):
    session_id: int
    status: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_at: datetime
    retry_after_ms: int
    remote_userid: str | None = None
    error_category: str | None = None


def get_account_data(user: UserProfile, platform: Platform):
    try:
        return getattr(user, PLATFORM_CONFIG[platform]['related_name'])
    except ObjectDoesNotExist:
        return None


@router.get('/{user_id}', response=AccountLinkCompleteOut)
@decorate_view(ratelimit(key='ip', rate='2/s'))
def get_account_links(request, user_id: int):
    """
    Return visible account links and include verified account details in one request.

    - ratelimit(key='ip', rate='2/s')
    - Staff and the user themself can see all links, including unverified and private links.
    - Other users can only see verified non-private links.
    - Platform account details are included only for verified visible links.
    """
    if not (user := UserProfile.objects.select_related(
        *[config['related_name'] for config in PLATFORM_CONFIG.values()],
    ).filter(id=user_id).first()):
        return HttpResponseNotFound()

    request_user = request.user
    can_view_private = request_user.is_staff or user == request_user

    accountlinks = AccountLinkQueue.objects.filter(userprofile=user).order_by('platform')
    if not can_view_private:
        accountlinks = accountlinks.filter(verified=True).exclude(platform__in=private_platforms)

    data = {
        'summary': list(accountlinks),
        Platform.BILIBILI.value: None,
        Platform.SAOLEI.value: None,
        Platform.MSGAMES.value: None,
        Platform.MINERACER.value: None,
        Platform.WOM.value: None,
        Platform.QQ.value: None,
    }

    for accountlink in accountlinks:
        if accountlink.verified:
            platform = Platform(accountlink.platform)
            data[platform.value] = get_account_data(user, platform)

    return data


@router.post('/create/', response=AccountLinkOut)
@decorate_view(
    login_required_error,
    ratelimit(key='user', rate='10/d'),
)
def create_account_link(request, data: AccountLinkCreateIn = Form(...)):  # noqa: B008
    """
    Create an account link for the current user and return the new queue item.

    - login_required_error
    - ratelimit(key='user', rate='10/d')
    - Each user can only have one link per platform.
    """
    if data.platform not in Platform.values or not data.identifier:
        return HttpResponseBadRequest()
    if data.platform == Platform.MINERACER:
        return HttpResponseBadRequest()
    if AccountLinkQueue.objects.filter(platform=data.platform, userprofile=request.user).exists():
        return HttpResponseConflict()
    return AccountLinkQueue.objects.create(
        platform=data.platform,
        identifier=data.identifier,
        userprofile=request.user,
    )


@router.post('/mineracer/start/', response=MineracerAccountLinkSessionOut)
@decorate_view(
    login_required_error,
    ratelimit(key='user', rate='6/h'),
)
def create_mineracer_account_link_session(request):
    """
    - login_required_error
    - ratelimit(key='user', rate='6/h')

    Create or reuse a pending Mineracer account-link session for the current user.
    """
    return mineracer_session_response(start_mineracer_account_link(request.user))


@router.get('/mineracer/status/{session_id}', response=MineracerAccountLinkSessionOut)
@decorate_view(
    login_required_error,
    ratelimit(key='user', rate='30/m'),
)
def get_mineracer_account_link_session(request, session_id: int):
    """
    - login_required_error
    - ratelimit(key='user', rate='30/m')

    Return the local Mineracer link session status and poll Mineracer when due.
    """
    session = poll_mineracer_account_link_session(request.user, session_id)
    if session is None:
        return HttpResponseNotFound()
    return mineracer_session_response(session)


def mineracer_session_response(session: MineracerAccountLinkSession):
    remote_userid = session.remote_userid or None
    error_category = session.error_category or None
    return {
        'session_id': session.id,
        'status': session.status,
        'user_code': session.user_code,
        'verification_uri': session.verification_uri,
        'verification_uri_complete': session.verification_uri_complete,
        'expires_at': session.expires_at,
        'retry_after_ms': get_mineracer_session_retry_after_ms(session),
        'remote_userid': remote_userid,
        'error_category': error_category,
    }


@router.get('/admin/queue', response=List[AccountLinkOut])
@decorate_view(staff_required)
def get_account_link_queue(request):
    return AccountLinkQueue.objects.all()
