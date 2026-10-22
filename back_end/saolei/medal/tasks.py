from django.tasks import task, TaskResultStatus
from django_tasks_db.models import DBTaskResult


@task(priority=10)
def task_refresh_player_medals(user_id: int):
    """重算该玩家已经接上的勋章。同一条任务覆盖这一名玩家。"""
    from .services import evaluate_player
    evaluate_player(user_id)
    return user_id


def enqueue_player_refresh(user_id: int):
    """同一玩家已有一条 READY 的刷新任务时不再插入。"""
    path = task_refresh_player_medals.module_path
    queued = DBTaskResult.objects.filter(task_path=path, status=TaskResultStatus.READY).values_list('args_kwargs', flat=True)
    for payload in queued:
        if isinstance(payload, dict) and payload.get('args') == [user_id]:
            return None
    return task_refresh_player_medals.enqueue(user_id)


@task(priority=0)
def task_backfill_player_medals(user_id: int):
    """按当前规则补发这一名玩家。优先级低于上传后的刷新。"""
    from .services import evaluate_player
    evaluate_player(user_id)
    return user_id


def enqueue_player_backfill(user_id: int):
    """同一玩家已有一条 READY 的补发任务时不再插入。"""
    path = task_backfill_player_medals.module_path
    queued = DBTaskResult.objects.filter(task_path=path, status=TaskResultStatus.READY).values_list('args_kwargs', flat=True)
    for payload in queued:
        if isinstance(payload, dict) and payload.get('args') == [user_id]:
            return None
    return task_backfill_player_medals.enqueue(user_id)
