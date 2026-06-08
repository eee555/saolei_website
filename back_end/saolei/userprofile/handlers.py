from corsheaders.signals import check_request_enabled
from django.http import HttpRequest


def cors_allow_api_userprofile(sender, request: HttpRequest, **kwargs):
    p = request.path
    if p.startswith('/api/userprofile/'):
        return p.startswith('videolist', 17) or p.startswith('info/', 17) or p.startswith('identifier', 17) or p.startswith('avatar/', 17)

    return False


check_request_enabled.connect(cors_allow_api_userprofile)
