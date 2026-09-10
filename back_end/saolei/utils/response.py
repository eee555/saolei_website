from django.http import HttpResponse, JsonResponse


def ratelimited_error(request, exception):
    return HttpResponse(status=429)


class HttpResponseConflict(HttpResponse):
    status_code = 409


def realname_required_response():
    return JsonResponse({'type': 'error', 'obj': 'userprofile', 'category': 'realname_required'})
