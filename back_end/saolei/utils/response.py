from django.http import HttpResponse

def ratelimited_error(request, exception):
    return HttpResponse(status=429)

class HttpResponseConflict(HttpResponse):
    status_code = 409