from django.core.management import call_command
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

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


@require_POST
@local_only
def quick_register(request: HttpRequest):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    user_id = request.POST.get('id')

    if not username or not email or not password or not id:
        return HttpResponse('missing_parameters', status=400)

    if UserProfile.objects.filter(username=username).exists():
        return HttpResponse('user_exists', status=409)
    if UserProfile.objects.filter(email=email).exists():
        return HttpResponse('email_exists', status=409)
    if UserProfile.objects.filter(id=user_id).exists():
        return HttpResponse('id_exists', status=409)

    UserProfile.objects.create_user(username=username, password=password, id=user_id, email=email)

    return HttpResponse('success')
