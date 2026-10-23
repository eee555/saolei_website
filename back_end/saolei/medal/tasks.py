from django.db import transaction
from django.tasks import task, TaskResultStatus
from django_tasks_db.models import DBTaskResult

from userprofile.models import UserProfile
from .services import evaluate_player


@task(priority=10)
def task_refresh_player_medals(user_id: int):
    """重算该玩家已经接上的勋章。同一条任务覆盖这一名玩家。"""
    evaluate_player(user_id)
    return user_id


def enqueue_player_refresh(user_id: int):
    """同一玩家已有一条 READY 的刷新任务时不再插入。"""
    return _enqueue_player_task(task_refresh_player_medals, user_id)


@task(priority=0)
def task_backfill_player_medals(user_id: int):
    """按当前规则补发这一名玩家。优先级低于上传后的刷新。"""
    evaluate_player(user_id)
    return user_id


def enqueue_player_backfill(user_id: int):
    """同一玩家已有一条 READY 的补发任务时不再插入。"""
    return _enqueue_player_task(task_backfill_player_medals, user_id)


def _enqueue_player_task(player_task, user_id):
    # Serialize producers for this player, including the empty-queue case.
    with transaction.atomic():
        if not UserProfile.objects.select_for_update().filter(pk=user_id).exists():
            return None
        if DBTaskResult.objects.filter(
            task_path=player_task.module_path, status=TaskResultStatus.READY,
            args_kwargs__args=[user_id],
        ).exists():
            return None
        return player_task.enqueue(user_id)
