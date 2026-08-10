from collections import defaultdict

from django.db.models import F, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from config.tournaments import GSC_Defaults
from tournament.models import GSCParticipant, GSCTournament
from tournament.services import award_tournament_rank_scores, delete_participants_without_videos, reveal_videos_for_tournament

GSC_SCORE_FIELDS = [
    'bt1st', 'bt20th', 'bt20sum',
    'it1st', 'it12th', 'it12sum',
    'et1st', 'et5th', 'et5sum',
]

GSC_LEVEL_RULES = {
    MS_TextChoices.Level.BEGINNER: {
        'first': 'bt1st',
        'edge': 'bt20th',
        'total': 'bt20sum',
        'default': GSC_Defaults.BT,
        'bv_min': GSC_Defaults.B_BV_MIN,
        'count': 20,
    },
    MS_TextChoices.Level.INTERMEDIATE: {
        'first': 'it1st',
        'edge': 'it12th',
        'total': 'it12sum',
        'default': GSC_Defaults.IT,
        'bv_min': GSC_Defaults.I_BV_MIN,
        'count': 12,
    },
    MS_TextChoices.Level.EXPERT: {
        'first': 'et1st',
        'edge': 'et5th',
        'total': 'et5sum',
        'default': GSC_Defaults.ET,
        'bv_min': GSC_Defaults.E_BV_MIN,
        'count': 5,
    },
}

GSC_SCORE_VALUE_FIELDS = [
    'id',
    'user__id',
    'user__realname',
    'start_time', 'end_time',
    'rank', 'rank_score',
    'bt1st', 'bt20th', 'bt20sum',
    'it1st', 'it12th', 'it12sum',
    'et1st', 'et5th', 'et5sum',
]


def _apply_gsc_scores(participant: GSCParticipant, times_by_level):
    for level, rule in GSC_LEVEL_RULES.items():
        times = sorted(times_by_level.get(level, []))[:rule['count']]
        default = rule['default']
        count = rule['count']

        setattr(participant, rule['first'], times[0] if times else default)
        setattr(participant, rule['edge'], times[count - 1] if len(times) >= count else default)
        setattr(participant, rule['total'], sum(times) + (count - len(times)) * default)


def refresh_gsc_scores(tournament: GSCTournament, *, batch_size=1000):
    """
    批量刷新 GSC 参赛者成绩。

    三个级别分别查询每个玩家的前若干条有效录像，在内存中合并为完整
    GSC 成绩，最后用 bulk_update 分批写回。
    """
    participants = list(GSCParticipant.objects.filter(tournament=tournament))
    if not participants:
        return 0

    participants_by_user_id = {
        participant.user_id: participant
        for participant in participants
        if participant.user_id is not None
    }
    times_by_user_id = defaultdict(lambda: defaultdict(list))

    for level, rule in GSC_LEVEL_RULES.items():
        ranked_videos = (
            tournament.videos
            .filter(level=level, bv__gte=rule['bv_min'], timems__lt=rule['default'])
            .annotate(
                gsc_row_number=Window(
                    expression=RowNumber(),
                    partition_by=[F('player_id')],
                    order_by=[F('timems').asc()],
                ),
            )
            .filter(gsc_row_number__lte=rule['count'])
            .values_list('player_id', 'timems')
        )

        for player_id, timems in ranked_videos.iterator(chunk_size=batch_size):
            if player_id not in participants_by_user_id:
                continue
            times_by_user_id[player_id][level].append(timems)

    for participant in participants:
        _apply_gsc_scores(participant, times_by_user_id.get(participant.user_id, {}))

    GSCParticipant.objects.bulk_update(participants, GSC_SCORE_FIELDS, batch_size=batch_size)

    return len(participants)


def refresh_gsc_ranks(tournament: GSCTournament, *, batch_size=1000):
    participants = list(GSCParticipant.objects.filter(tournament=tournament).order_by('t37'))
    for rank, participant in enumerate(participants, start=1):
        participant.rank = rank

    GSCParticipant.objects.bulk_update(participants, ['rank'], batch_size=batch_size)

    return len(participants)


def refresh_gsc_scores_and_ranks(tournament: GSCTournament):
    score_changed = refresh_gsc_scores(tournament)
    rank_changed = refresh_gsc_ranks(tournament)
    return {
        'score_changed': score_changed,
        'rank_changed': rank_changed,
    }


def finish_gsc_tournament(tournament: GSCTournament):
    deleted_participants = delete_participants_without_videos(tournament)
    result = refresh_gsc_scores_and_ranks(tournament)
    result['deleted_participants'] = deleted_participants
    result['awarded_participants'] = award_tournament_rank_scores(tournament)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        tournament.state = Tournament_TextChoices.State.AWARDED
        tournament.save(update_fields=['state'])
    result['revealed_videos'] = reveal_videos_for_tournament(tournament)
    return result


def get_gsc_scores(tournament: GSCTournament):
    return GSCParticipant.objects.filter(tournament=tournament).select_related('user')
