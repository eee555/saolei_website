from django.tasks import task

from utils.exceptions import ExceptionToResponse


# Keep old task paths resolvable so queued jobs fail without fetching or enqueueing.
@task(priority=-1)
def task_saolei_video_import(video_id: int):
    raise ExceptionToResponse('saolei', 'crawling_disabled', status_code=410)


@task
def task_saolei_profile(saolei_id: int):
    raise ExceptionToResponse('saolei', 'crawling_disabled', status_code=410)


@task(priority=2)
def task_saolei_video_import_bulk(saolei_id: int, mode: str):
    raise ExceptionToResponse('saolei', 'crawling_disabled', status_code=410)
