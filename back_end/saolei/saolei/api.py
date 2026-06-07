from ninja import NinjaAPI, Redoc

from accountlink.api import router as accountlink_router
from common.api import router as common_router
from userprofile.api import router as userprofile_router
from utils.exceptions import ExceptionToResponse
from videomanager.api import router as videomanager_router

api = NinjaAPI(docs=Redoc())

api.add_router('/common/', common_router)
api.add_router('/userprofile/', userprofile_router)
api.add_router('/accountlink/', accountlink_router)
api.add_router('/video/', videomanager_router)


@api.exception_handler(ExceptionToResponse)
def general_exception(request, exc: ExceptionToResponse):
    return exc.response()
