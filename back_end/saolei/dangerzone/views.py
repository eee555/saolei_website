from django.core.management import call_command
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from msuser.models import UserMS
from rest_framework.decorators import api_view
from rest_framework.request import Request
from userprofile.decorators import login_required_error
from userprofile.models import UserProfile
from .decorators import local_only


@require_POST
@local_only
@login_required_error
def delete_user(request: HttpRequest):
    request.user.delete()
    return HttpResponse()


@require_POST
@local_only
def flush_database(request: HttpRequest):
    call_command('flush', interactive=False)
    return HttpResponse()


@api_view(['POST'])
@local_only
def quick_register(request: Request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_id = data.get('id')

    if not username or not email or not password or not user_id:
        return HttpResponse(f'missing_parameters. username={username}, email={email}, password={password}, user_id={user_id}', status=400)

    if UserProfile.objects.filter(username=username).exists():
        return HttpResponse('user_exists', status=409)
    if UserProfile.objects.filter(email=email).exists():
        return HttpResponse('email_exists', status=409)
    if UserProfile.objects.filter(id=user_id).exists():
        return HttpResponse('id_exists', status=409)

    userms = UserMS.objects.create()
    UserProfile.objects.create_user(username=username, password=password, id=user_id, email=email, userms=userms)

    return HttpResponse('success')
