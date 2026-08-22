from functools import wraps

from django.http import HttpResponseForbidden

from config.tournaments import GSC_Defaults


def GSC_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.id == GSC_Defaults.HOST_ID:
            return HttpResponseForbidden()  # Return 403 Forbidden response
        return view_func(request, *args, **kwargs)  # Call the view if not banned
    return _wrapped_view
