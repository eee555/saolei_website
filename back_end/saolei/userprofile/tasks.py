

from django_tasks import task

from .services import update_cache_realname


@task
def task_user_update_realname(user_id: int, user_realname: str):
    update_cache_realname(user_id, user_realname)
