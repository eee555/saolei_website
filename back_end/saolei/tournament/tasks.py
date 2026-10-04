from django.tasks import task

from .models import Tournament
from .services import award_tournament_rank_scores, ensure_tournament_users


def _task_award_tournament_impl(tournament_id: int):
    tournament = Tournament.objects.get(id=tournament_id)
    ensure_tournament_users(tournament)
    return award_tournament_rank_scores(tournament)


@task
def task_award_tournament(tournament_id: int):
    return _task_award_tournament_impl(tournament_id)
