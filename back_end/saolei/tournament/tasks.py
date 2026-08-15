from django.tasks import task

from .models import Tournament
from .services import award_tournament_rank_scores, create_tournament_users_for_tournament


def _task_award_tournament_impl(tournament_id: int):
    tournament = Tournament.objects.get(id=tournament_id)
    tournament_users = create_tournament_users_for_tournament(tournament)
    return award_tournament_rank_scores(tournament, tournament_users=tournament_users)


@task
def task_award_tournament(tournament_id: int):
    return _task_award_tournament_impl(tournament_id)
