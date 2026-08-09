from django.tasks import task
from django_tasks import TaskResultStatus

from tournament.models import WeeklyTournament
from .services import finish_weekly_tournament


def helper_weekly_finish_tournament(tournament: WeeklyTournament):
    existing_task = tournament.task
    if existing_task:
        if existing_task.status == TaskResultStatus.SUCCESSFUL:
            existing_task.delete()
        elif existing_task.status in [TaskResultStatus.READY, TaskResultStatus.RUNNING]:
            return existing_task

    tournament.task = task_weekly_finish.enqueue(tournament.id).db_result
    tournament.save(update_fields=['task'])
    return tournament.task


@task
def task_weekly_finish(tournament_id: int):
    tournament = WeeklyTournament.objects.get(id=tournament_id)
    return finish_weekly_tournament(tournament)
