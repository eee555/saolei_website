
from django.conf import settings
from django_ratelimit.decorators import ratelimit


def ratelimit_testaware(*args, **kwargs):
    """
    A wrapper around django_ratelimit.decorators.ratelimit that
    disables rate limiting when settings.E2E_TEST is True.
    """
    if getattr(settings, "E2E_TEST", False):
        # Return a no-op decorator
        def noop_decorator(view_func):
            return view_func
        return noop_decorator
    else:
        # Return the original ratelimit decorator
        return ratelimit(*args, **kwargs)
