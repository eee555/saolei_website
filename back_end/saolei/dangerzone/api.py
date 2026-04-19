from django.core.management import call_command
from django_redis import get_redis_connection
from ninja import NinjaAPI, Schema

from msuser.models import UserMS
from userprofile.models import UserProfile
from .decorators import local_only

api = NinjaAPI()


class UserIdSchema(Schema):
    id: int


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


@api.post('/setstaff')
@local_only
def set_staff(request, data: UserIdSchema):
    user = UserProfile.objects.get(id=data.id)
    user.is_staff = True
    user.save()
