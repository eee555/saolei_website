import socket
from functools import wraps
from django.http import HttpResponseForbidden
from django.conf import settings


def local_only(view_func):
    """
    Decorator to allow only requests from the same server (localhost or server's IP).
    """
    try:
        SERVER_IP = socket.gethostbyname(socket.gethostname())
    except Exception:
        SERVER_IP = None

    ALLOWED_IPS = {"127.0.0.1", "::1"}
    if SERVER_IP:
        ALLOWED_IPS.add(SERVER_IP)

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check E2E_TEST flag
        if not settings.E2E_TEST:
            return HttpResponseForbidden("Forbidden: E2E_TEST mode is not enabled.")

        client_ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
        if client_ip not in ALLOWED_IPS:
            return HttpResponseForbidden(f"Forbidden: Access from {client_ip} is not allowed.")
        return view_func(request, *args, **kwargs)

    _wrapped_view._local_only = True  # Marker for testing
    return _wrapped_view
