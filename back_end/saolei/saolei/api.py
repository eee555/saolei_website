from ninja import NinjaAPI, Redoc

from common.api import router as common_router
from userprofile.api import router as userprofile_router
from utils.exceptions import ExceptionToResponse

api = NinjaAPI(docs=Redoc())

api.add_router('/common/', common_router)
api.add_router('/userprofile/', userprofile_router)


@api.exception_handler(ExceptionToResponse)
def general_exception(request, exc: ExceptionToResponse):
    return exc.response()
