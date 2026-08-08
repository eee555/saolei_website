from ninja import NinjaAPI, Redoc

from accountlink.api import router as accountlink_router
from common.api import router as common_router
from customranking.api import router as customranking_router
from msuser.api import router as msuser_router
from tournament.api import router as tournament_router
from tournament.gsc.api import router as tournament_gsc_router
from tournament.weekly.api import router as tournament_weekly_router
from userprofile.api import router as userprofile_router
from utils.exceptions import ExceptionToResponse
from videomanager.api import router as videomanager_router

api = NinjaAPI(docs=Redoc())

api.add_router('/common/', common_router)
api.add_router('/userprofile/', userprofile_router)
api.add_router('/accountlink/', accountlink_router)
api.add_router('/video/', videomanager_router)
api.add_router('/customranking/', customranking_router)
api.add_router('/msuser/', msuser_router)
api.add_router('/tournament/', tournament_router)
api.add_router('/tournament/gsc/', tournament_gsc_router)
api.add_router('/tournament/weekly/', tournament_weekly_router)


@api.exception_handler(ExceptionToResponse)
def general_exception(request, exc: ExceptionToResponse):
    return exc.response()
