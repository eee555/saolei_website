from django.db.models import F, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from tournament.models import TournamentUser, WeeklyParticipant, WeeklyTournament
from tournament.services import award_tournament_rank_scores, delete_participants_without_videos, reveal_videos_for_tournament
from tournament.utils import encode_tournament_best
from .utils import weekly_encode_best


def refresh_weekly_classic_scores(tournament: WeeklyTournament, *, batch_size=1000):
    """
    批量刷新 周赛-2高5中 成绩。
    """
    participants = list(WeeklyParticipant.objects.filter(tournament=tournament))
    if not participants:
        return 0

    participants_by_user_id = {
        participant.user_id: participant
        for participant in participants
        if participant.user_id is not None
    }

    ranked_exp = tournament.videos.filter(level=MS_TextChoices.Level.EXPERT, timems__lt=240000).annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F('player_id')],
            order_by='timems',
        ),
    ).filter(row_number__lte=2).values_list('id', 'player_id', 'timems')
    for video_id, player_id, timems in ranked_exp.iterator(chunk_size=batch_size):
        if player_id not in participants_by_user_id:
            continue
        participants_by_user_id[player_id].classic_add_e(video_id, timems)

    ranked_int = tournament.videos.filter(level=MS_TextChoices.Level.INTERMEDIATE, timems__lt=60000).annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F('player_id')],
            order_by='timems',
        ),
    ).filter(row_number__lte=5).values_list('id', 'player_id', 'timems')
    for video_id, player_id, timems in ranked_int.iterator(chunk_size=batch_size):
        if player_id not in participants_by_user_id:
            continue
        participants_by_user_id[player_id].classic_add_i(video_id, timems)

    WeeklyParticipant.objects.bulk_update(participants, ['classic_et', 'classic_it', 'classic_score'], batch_size=batch_size)

    return len(participants)


def refresh_weekly_classic_ranks(tournament: WeeklyTournament, *, batch_size=1000):
    participants = list(WeeklyParticipant.objects.filter(tournament=tournament).order_by('classic_score'))
    for rank, participant in enumerate(participants, start=1):
        participant.rank = rank

    WeeklyParticipant.objects.bulk_update(participants, ['rank'], batch_size=batch_size)

    return len(participants)


def finish_weekly_tournament(tournament: WeeklyTournament):
    deleted_participants = delete_participants_without_videos(tournament)
    score_count = refresh_weekly_classic_scores(tournament)
    rank_count = refresh_weekly_classic_ranks(tournament)
    award_count = award_tournament_rank_scores(tournament)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        tournament.state = Tournament_TextChoices.State.AWARDED
        tournament.save(update_fields=['state'])
    video_count = reveal_videos_for_tournament(tournament)
    return {
        'deleted_participants': deleted_participants,
        'score_count': score_count,
        'rank_count': rank_count,
        'award_count': award_count,
        'video_count': video_count,
    }


def update_weekly_best_score_from_participant(tournament_user: TournamentUser, participant: WeeklyParticipant) -> list[str]:
    if participant.user_id is None or participant.rank_score <= 0:
        return []

    tournament = participant.tournament.weeklytournament
    new_best = weekly_encode_best(participant.classic_score, tournament.year, tournament.week)
    if tournament_user.weekly_best != 0 and tournament_user.weekly_best <= new_best:
        return []

    tournament_user.weekly_best = new_best
    return ['weekly_best']


def calculate_weekly_best_score(user_id: int):
    best_participant = (
        WeeklyParticipant.objects
        .filter(user_id=user_id, rank_score__gt=0)
        .select_related('tournament__weeklytournament')
        .order_by('classic_score', 'tournament__weeklytournament__year', 'tournament__weeklytournament__week')
        .first()
    )
    if best_participant is None:
        return 0
    tournament = best_participant.tournament.weeklytournament
    return weekly_encode_best(best_participant.classic_score, tournament.year, tournament.week)
