from django.http import HttpResponse

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

# 账号或密码错误
class HttpResponsePasswordMismatch(HttpResponse):
    status_code = 701

# 验证码错误
class HttpResponseCaptchaMismatch(HttpResponse):
    status_code = 702

def ratelimited_error(request, exception):
    return HttpResponseTooManyRequests()