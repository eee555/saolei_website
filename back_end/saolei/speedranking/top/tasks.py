from django.tasks import task, TaskContext, TaskResultStatus
from django_tasks_db.models import DBTaskResult

from .services import rebuild_soft_ranks


@task(takes_context=True)
def task_refresh_soft_ranks(context: TaskContext):
    """有同类排队任务则交给后续任务，否则按最新锚点重建。"""
    pending = DBTaskResult.objects.filter(task_path='speedranking.top.tasks.task_refresh_soft_ranks', status=TaskResultStatus.READY).exclude(pk=context.task_result.id)
    if pending.exists():
        return {'skipped': True}
    return {'players': rebuild_soft_ranks()}
