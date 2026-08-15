from django.tasks import task

from .models import Tournament
from .services import award_tournament_rank_scores


def _task_award_tournament_impl(tournament_id: int):
    tournament = Tournament.objects.get(id=tournament_id)
    return award_tournament_rank_scores(tournament)


@task
def task_award_tournament(tournament_id: int):
    return _task_award_tournament_impl(tournament_id)
