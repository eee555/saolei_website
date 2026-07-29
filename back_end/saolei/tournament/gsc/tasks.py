from django.tasks import task

from config.text_choices import Tournament_TextChoices
from tournament.models import GSCTournament
from tournament.services import reveal_videos_for_tournament
from .services import refresh_gsc_ranks, refresh_gsc_scores


def refresh_gsc_scores_and_ranks(tournament: GSCTournament):
    score_changed = refresh_gsc_scores(tournament)
    rank_changed = refresh_gsc_ranks(tournament)
    return {
        'score_changed': score_changed,
        'rank_changed': rank_changed,
    }


@task
def task_gsc_refresh(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    return refresh_gsc_scores_and_ranks(tournament)


@task
def task_gsc_finish(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    result = refresh_gsc_scores_and_ranks(tournament)
    result['revealed_videos'] = reveal_videos_for_tournament(tournament)
    tournament.state = Tournament_TextChoices.State.AWARDED
    tournament.save(update_fields=['state'])
    return result
