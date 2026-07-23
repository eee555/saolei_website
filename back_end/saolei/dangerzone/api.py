from django.core.management import call_command
from django_redis import get_redis_connection
from ninja import NinjaAPI, Schema

from msuser.models import UserMS
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


@api.post('/register')
@local_only
def register(request, data: RegisterSchema):
    userms = UserMS.objects.create()
    UserProfile.objects.create_user(username=data.username, password=data.password, id=data.id, email=data.email, userms=userms)


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


@api.post('/setstaff')
@local_only
def set_staff(request, data: UserIdSchema):
    user = UserProfile.objects.get(id=data.id)
    user.is_staff = True
    user.save(update_fields=['is_staff'])
