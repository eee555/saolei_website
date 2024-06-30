from django.http import HttpResponse

def ratelimited_error(request, exception):
    return HttpResponse(status=429)