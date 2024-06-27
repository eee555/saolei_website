from django.http import JsonResponse

def StatusResponse(status, msg=""):
    if msg == "":
        return JsonResponse({'status': status})
    else:
        return JsonResponse({'status': status, 'message': msg})

### List of Statuses ###

## 1xx - Success
# 100 - General Success

## 2xx - Error
# 200 - General Error
# 201 - Permission Denied
# 202 - Backend Error
# 203 - Unrecognised Request

def SuccessResponse(msg=""):
    return StatusResponse(100, msg)

def ErrorResponse(msg=""):
    return StatusResponse(200, msg)

def PermissionDeniedResponse(msg=""):
    return StatusResponse(201, msg)

def BackendErrorResponse(msg=""):
    return StatusResponse(202, msg)

def UnrecognisedRequestResponse(msg=""):
    return StatusResponse(203, msg)