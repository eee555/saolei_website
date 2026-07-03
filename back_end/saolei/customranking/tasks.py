from django.tasks import task

from .services import refresh_all_custom_pluck_ranks


@task(priority=2)
def task_refresh_all_custom_pluck_ranks():
    return refresh_all_custom_pluck_ranks()
