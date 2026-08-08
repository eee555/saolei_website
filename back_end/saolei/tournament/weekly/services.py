
from collections import defaultdict

from django.db.models import F, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from tournament.models import WeeklyParticipant, WeeklyTournament
from tournament.services import delete_participants_without_videos, reveal_videos_for_tournament


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
    for video in ranked_exp.iterator(chunk_size=batch_size):
        if video.player_id not in participants_by_user_id:
            continue
        participants_by_user_id[video.player_id].classic_add_e(video.id, video.timems)

    ranked_int = tournament.videos.filter(level=MS_TextChoices.Level.INTERMEDIATE, timems__lt=60000).annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F('player_id')],
            order_by='timems',
        ),
    ).filter(row_number__lte=5).values_list('id', 'player_id', 'timems')
    for video in ranked_int.iterator(chunk_size=batch_size):
        if video.player_id not in participants_by_user_id:
            continue
        participants_by_user_id[video.player_id].classic_add_i(video.id, video.timems)

    WeeklyParticipant.objects.bulk_update(participants, ['classic_et', 'classic_it', 'classic_score'], batch_size=batch_size)

    return len(participants)


def refresh_weekly_classic_ranks(tournament: WeeklyTournament, *, batch_size=1000):
    participants = list(WeeklyParticipant.objects.filter(tournament=tournament).order_by('classic_score'))
    for rank, participant in enumerate(participants, start=1):
        participant.rank = rank
        participant.rank_score = 50 / rank

    WeeklyParticipant.objects.bulk_update(participants, ['rank', 'rank_score'], batch_size=batch_size)

    return len(participants)


def finish_weekly_tournament(tournament: WeeklyTournament):
    deleted_participants = delete_participants_without_videos(tournament)
    score_count = refresh_weekly_classic_scores(tournament)
    rank_count = refresh_weekly_classic_ranks(tournament)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        tournament.state = Tournament_TextChoices.State.AWARDED
        tournament.save(update_fields=['state'])
    video_count = reveal_videos_for_tournament(tournament)
    return {score_count, rank_count, video_count}
