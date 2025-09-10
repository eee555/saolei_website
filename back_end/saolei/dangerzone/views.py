from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.management import call_command
from userprofile.decorators import login_required_error
from .decorators import local_only


@require_POST
@local_only
@login_required_error
def delete_user(request):
    request.user.delete()
    return HttpResponse()


@require_POST
@local_only
def flush_database(request):
    call_command('flush', interactive=False)
    return HttpResponse()
