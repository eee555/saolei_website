from ninja import NinjaAPI

from userprofile.decorators import staff_required
from .tasks import task_gsc_refresh

api = NinjaAPI()


@api.post(path='/gsc/refreshscore')
@staff_required
def api_gsc_refreshscore(request, order):
    return task_gsc_refresh.enqueue(order).db_result.id
