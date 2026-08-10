from datetime import datetime

from django.core.management import call_command
from django_redis import get_redis_connection
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError

from common.api import LOG_DIR
from config.text_choices import Tournament_TextChoices
from config.tournaments import TournamentWeights
from identifier.models import Identifier
from identifier.services import bind_identifier, set_safe, unbind_identifier
from msuser.models import UserMS
from tournament.models import GSCTournament
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .decorators import local_only

api = NinjaAPI()


class UserIdSchema(Schema):
    id: int


class CreateVideoSchema(Schema):
    user_id: int
    timems: int
    bv: int
    state: str = 'd'
    software: str = 'e'
    level: str = 'e'
    mode: str = '00'
    identifier: str = 'dangerzone'
    file_size: int = 1024
    left: int = 100
    right: int = 50
    double: int = 25
    left_ce: int = 100
    right_ce: int = 50
    double_ce: int = 25
    path: float = 1000
    pluck: float | None = None


class IdentifierSchema(Schema):
    identifier: str
    safe: bool = True


class UserIdentifierSchema(Schema):
    user_id: int
    identifier: str
    safe: bool = True


class WriteLogSchema(Schema):
    filename: str
    content: str
    append: bool = False


class CreateGSCTournamentSchema(Schema):
    order: int
    state: str = 'n'
    start_time: datetime | None = None
    end_time: datetime | None = None
    token: str = ''
    host_id: int | None = None


@api.post('/flush_database')
@local_only
def flush_database(request):
    call_command('flush', interactive=False)
    get_redis_connection('saolei_website').flushdb()


class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    id: int
    realname: str = '匿名'


@api.post('/register')
@local_only
def register(request, data: RegisterSchema):
    userms = UserMS.objects.create()
    UserProfile.objects.create_user(
        username=data.username,
        password=data.password,
        id=data.id,
        email=data.email,
        realname=data.realname,
        userms=userms,
    )


@api.post('/create_video')
@local_only
def create_video(request, data: CreateVideoSchema):
    user = UserProfile.objects.get(id=data.user_id)
    expand_video = ExpandVideoModel.objects.create(identifier=data.identifier)
    video = VideoModel.objects.create(
        player=user,
        file=f'videos/dangerzone/{data.user_id}_{data.timems}_{data.bv}.evf',
        file_size=data.file_size,
        video=expand_video,
        state=data.state,
        software=data.software,
        level=data.level,
        mode=data.mode,
        timems=data.timems,
        bv=data.bv,
        left=data.left,
        right=data.right,
        double=data.double,
        left_ce=data.left_ce,
        right_ce=data.right_ce,
        double_ce=data.double_ce,
        path=data.path,
        pluck=data.pluck,
    )
    return {'id': video.id}


@api.post('/create_gsc_tournament')
@local_only
def create_gsc_tournament(request, data: CreateGSCTournamentSchema):
    host = UserProfile.objects.filter(id=data.host_id).first() if data.host_id is not None else None
    tournament, _ = GSCTournament.objects.update_or_create(
        order=data.order,
        defaults={
            'state': data.state,
            'start_time': data.start_time,
            'end_time': data.end_time,
            '_token': data.token,
            'host': host,
            'weight': TournamentWeights.GSC,
        },
    )
    return {
        'id': tournament.id,
        'subclass': Tournament_TextChoices.Subclass.GSC,
        'state': tournament.state,
        'start_time': tournament.start_time,
        'end_time': tournament.end_time,
        'host_id': tournament.host_id,
        'data': tournament.data,
    }


@api.post('/create_identifier')
@local_only
def create_identifier(request, data: IdentifierSchema):
    identifier, _ = Identifier.objects.get_or_create(
        identifier=data.identifier,
        defaults={'safe': data.safe},
    )
    try:
        set_safe(identifier, data.safe)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {
        'identifier': identifier.identifier,
        'safe': identifier.safe,
        'userms_id': identifier.userms_id,
    }


@api.post('/bind_identifier')
@local_only
def bind_identifier_to_user(request, data: UserIdentifierSchema):
    user = UserProfile.objects.select_related('userms').get(id=data.user_id)
    identifier, _ = Identifier.objects.get_or_create(
        identifier=data.identifier,
        defaults={'safe': data.safe},
    )
    if data.safe and not identifier.safe:
        set_safe(identifier, True)

    try:
        changed_count = bind_identifier(identifier, user.userms)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {
        'identifier': identifier.identifier,
        'safe': identifier.safe,
        'user_id': user.id,
        'changed_count': changed_count,
    }


@api.post('/unbind_identifier')
@local_only
def unbind_identifier_from_user(request, data: UserIdentifierSchema):
    user = UserProfile.objects.select_related('userms').get(id=data.user_id)
    try:
        identifier = Identifier.objects.get(identifier=data.identifier)
        changed_count = unbind_identifier(identifier, user.userms)
    except Identifier.DoesNotExist as error:
        raise HttpError(404, 'Identifier not found') from error
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {
        'identifier': identifier.identifier,
        'user_id': user.id,
        'changed_count': changed_count,
    }


@api.post('/delete_identifier')
@local_only
def delete_identifier(request, data: IdentifierSchema):
    try:
        identifier = Identifier.objects.get(identifier=data.identifier)
    except Identifier.DoesNotExist:
        return {
            'identifier': data.identifier,
            'deleted': False,
            'changed_count': 0,
        }

    changed_count = 0
    if identifier.userms_id is not None:
        changed_count = unbind_identifier(identifier)
    identifier.delete()
    return {
        'identifier': data.identifier,
        'deleted': True,
        'changed_count': changed_count,
    }


@api.post('/setstaff')
@local_only
def set_staff(request, data: UserIdSchema):
    user = UserProfile.objects.get(id=data.id)
    user.is_staff = True
    user.save(update_fields=['is_staff'])


@api.post('/write_log')
@local_only
def write_log(request, data: WriteLogSchema):
    if data.filename != data.filename.split('/')[-1].split('\\')[-1]:
        raise HttpError(400, 'Invalid filename')

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / data.filename
    mode = 'a' if data.append else 'w'
    with log_path.open(mode, encoding='utf-8') as file:
        file.write(data.content)
    return {'name': data.filename, 'size': log_path.stat().st_size}
