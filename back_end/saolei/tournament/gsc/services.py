from collections import defaultdict

from django.utils import timezone
from django.db.models import F, Q, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from config.tournaments import GSC_Defaults
from tournament.services import reveal_videos_for_tournament
from tournament.models import GSCParticipant, GSCTournament

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

GSC_MAX_COUNT = max(rule['count'] for rule in GSC_LEVEL_RULES.values())

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


def _gsc_video_score_filter():
    filters = Q()
    for level, rule in GSC_LEVEL_RULES.items():
        filters |= Q(
            level=level,
            bv__gte=rule['bv_min'],
            timems__lt=rule['default'],
        )
    return filters


def _apply_gsc_scores(participant: GSCParticipant, times_by_level):
    for level, rule in GSC_LEVEL_RULES.items():
        times = sorted(times_by_level.get(level, []))[:rule['count']]
        default = rule['default']
        count = rule['count']

        setattr(participant, rule['first'], times[0] if times else default)
        setattr(participant, rule['edge'], times[count - 1] if len(times) >= count else default)
        setattr(participant, rule['total'], sum(times) + (count - len(times)) * default)


def refresh_gsc_participant_score(participant: GSCParticipant):
    times_by_level = defaultdict(list)
    videos = (
        participant.videos
        .filter(_gsc_video_score_filter())
        .order_by('level', 'timems', 'upload_time', 'id')
        .values_list('level', 'timems')
    )
    for level, timems in videos:
        rule = GSC_LEVEL_RULES.get(level)
        if rule is None or len(times_by_level[level]) >= rule['count']:
            continue
        times_by_level[level].append(timems)

    _apply_gsc_scores(participant, times_by_level)
    participant.save(update_fields=GSC_SCORE_FIELDS)
    return participant


def refresh_gsc_scores(tournament: GSCTournament, *, batch_size=1000):
    """
    批量刷新 GSC 参赛者成绩。

    一次取出每个 (玩家, 级别) 的前若干条有效录像，在内存中按 GSC 规则
    补足默认成绩，最后用 bulk_update 分批写回。
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

    ranked_videos = (
        tournament.videos
        .filter(_gsc_video_score_filter())
        .annotate(
            gsc_row_number=Window(
                expression=RowNumber(),
                partition_by=[F('player_id'), F('level')],
                order_by=[F('timems').asc(), F('upload_time').asc(), F('id').asc()],
            ),
        )
        .filter(gsc_row_number__lte=GSC_MAX_COUNT)
        .values_list('player_id', 'level', 'timems', 'gsc_row_number')
    )

    for player_id, level, timems, row_number in ranked_videos.iterator(chunk_size=batch_size):
        if player_id not in participants_by_user_id:
            continue
        rule = GSC_LEVEL_RULES.get(level)
        if rule is None or row_number > rule['count']:
            continue
        times_by_user_id[player_id][level].append(timems)

    changed_participants = []
    for participant in participants:
        old_scores = tuple(getattr(participant, field) for field in GSC_SCORE_FIELDS)
        _apply_gsc_scores(participant, times_by_user_id.get(participant.user_id, {}))
        new_scores = tuple(getattr(participant, field) for field in GSC_SCORE_FIELDS)
        if new_scores != old_scores:
            changed_participants.append(participant)

    if changed_participants:
        GSCParticipant.objects.bulk_update(changed_participants, GSC_SCORE_FIELDS, batch_size=batch_size)

    return len(changed_participants)


def refresh_gsc_ranks(tournament: GSCTournament, *, batch_size=1000):
    participants = list(GSCParticipant.objects.filter(tournament=tournament).order_by('t37', 'id'))
    changed_participants = []
    for rank, participant in enumerate(participants, start=1):
        if participant.rank == rank:
            continue
        participant.rank = rank
        changed_participants.append(participant)

    if changed_participants:
        GSCParticipant.objects.bulk_update(changed_participants, ['rank'], batch_size=batch_size)

    return len(changed_participants)


def refresh_gsc_scores_and_ranks(tournament: GSCTournament):
    score_changed = refresh_gsc_scores(tournament)
    rank_changed = refresh_gsc_ranks(tournament)
    return {
        'score_changed': score_changed,
        'rank_changed': rank_changed,
    }


def finish_gsc_tournament(tournament: GSCTournament):
    result = refresh_gsc_scores_and_ranks(tournament)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        tournament.state = Tournament_TextChoices.State.AWARDED
        tournament.save(update_fields=['state'])
    result['revealed_videos'] = reveal_videos_for_tournament(tournament)
    return result


def get_gsc_scores(tournament: GSCTournament):
    return GSCParticipant.objects.filter(tournament=tournament).values(*GSC_SCORE_VALUE_FIELDS)


def visible_gsc_token(tournament: GSCTournament):
    if tournament.start_time is None or timezone.now() < tournament.start_time:
        return ''
    return tournament.token
