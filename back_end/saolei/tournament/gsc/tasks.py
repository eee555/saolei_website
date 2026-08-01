from django.tasks import task
from django_tasks import TaskResultStatus

from tournament.models import GSCTournament
from .services import finish_gsc_tournament


def helper_gsc_finish_tournament(tournament: GSCTournament):
    existing_task = tournament.task
    if existing_task:
        if existing_task.status == TaskResultStatus.SUCCESSFUL:
            existing_task.delete()
        elif existing_task.status in [TaskResultStatus.READY, TaskResultStatus.RUNNING]:
            return existing_task

    tournament.task = task_gsc_finish.enqueue(tournament.order).db_result
    tournament.save(update_fields=['task'])
    return tournament.task


@task
def task_gsc_finish(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    return finish_gsc_tournament(tournament)
