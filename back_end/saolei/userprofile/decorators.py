from functools import wraps
from django.http import HttpResponseForbidden


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden()  # Return 403 Forbidden response
        return view_func(request, *args, **kwargs)  # Call the view if not banned
    return _wrapped_view


def banned_blocked(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_banned:
            return HttpResponseForbidden()  # Return 403 Forbidden response
        return view_func(request, *args, **kwargs)  # Call the view if not banned
    return _wrapped_view


def login_required_error(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()  # Return 403 Forbidden response
        return view_func(request, *args, **kwargs)  # Call the view if not banned
    return _wrapped_view
