from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from .models import AccountBilibili, AccountLinkQueue, AccountMinesweeperGames, AccountQQ, AccountSaolei, AccountWorldOfMinesweeper, Platform, PLATFORM_CONFIG
from utils.response import HttpResponseConflict
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
AccountQQOut = create_schema(AccountQQ)


class AccountLinkCompleteOut(Schema):
    summary: list[AccountLinkQueueOut]
    B: AccountBiliOut | None = None
    c: AccountSaoleiOut | None = None
    a: AccountMSGamesOut | None = None
    w: AccountWoMOut | None = None
    q: AccountQQOut | None = None


class AccountLinkCreateIn(Schema):
    platform: str
    identifier: str


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
    if AccountLinkQueue.objects.filter(platform=data.platform, userprofile=request.user).exists():
        return HttpResponseConflict()
    return AccountLinkQueue.objects.create(
        platform=data.platform,
        identifier=data.identifier,
        userprofile=request.user,
    )


@router.get('/admin/queue', response=List[AccountLinkOut])
@decorate_view(staff_required)
def get_account_link_queue(request):
    return AccountLinkQueue.objects.all()
