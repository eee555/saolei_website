from django.http import HttpResponse, JsonResponse

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

def ratelimited_error(request, exception):
    return HttpResponseTooManyRequests()


def SuccessResponse(data):
    return JsonResponse({'status': 100, 'data': data})

# 账号或密码错误
def PasswordMismatchException():
    return JsonResponse({'status': 201})

# 验证码错误
def CaptchaMismatchException():
    return JsonResponse({'status': 202})