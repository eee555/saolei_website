from collections import defaultdict
import logging

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from django_tasks_db.models import DBTaskResult

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from config.tournaments import GSC_Defaults
from tournament.cache import TournamentCache
from tournament.gsc.utils import gsc_encode_best
from tournament.models import GSCParticipant, GSCTournament, TournamentUser
from tournament.services import refresh_tournament_ranks
from tournament.utils import MAX_TOURNAMENT_BEST
from utils.exceptions import ExceptionToResponse

GSC_SCORE_FIELDS = [
    'bt1st', 'bt20th', 'bt20sum',
    'it1st', 'it12th', 'it12sum',
    'et1st', 'et5th', 'et5sum',
]

logger = logging.getLogger('tournament')
tournament_cache = TournamentCache()
GSC_FINISH_TASK_PATH = 'tournament.gsc.tasks.task_gsc_finish'

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


def restart_gsc_task(db_task: DBTaskResult, args: list, kwargs: dict):
    if db_task.task_path != GSC_FINISH_TASK_PATH:
        return None

    gsc_order = kwargs.get('gsc_order', args[0] if args else None)
    if gsc_order is None:
        raise ExceptionToResponse('task_restart', 'invalid_args', status_code=400)

    current_reference = (
        GSCTournament.objects
        .select_for_update()
        .filter(order=gsc_order, task_id=db_task.id)
        .first()
    )
    if current_reference is None:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)

    new_db_task = db_task.task.enqueue(*args, **kwargs).db_result
    updated_count = (
        GSCTournament.objects
        .filter(order=gsc_order, task_id=db_task.id)
        .update(task_id=new_db_task.id)
    )
    if not updated_count:
        raise ExceptionToResponse('task_restart', 'stale_reference', status_code=409)
    return new_db_task


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
    logger.info(f'GSC#{tournament.order} 成绩刷新开始，比赛#{tournament.id}')
    participants = list(GSCParticipant.objects.filter(tournament=tournament))
    if not participants:
        logger.info(f'GSC#{tournament.order} 成绩刷新跳过，没有参赛者')
        return 0
    logger.info(f'GSC#{tournament.order} 成绩刷新参赛者读取完成，数量 {len(participants)}')

    participants_by_user_id = {
        participant.user_id: participant
        for participant in participants
        if participant.user_id is not None
    }
    times_by_user_id = defaultdict(lambda: defaultdict(list))

    for level, rule in GSC_LEVEL_RULES.items():
        matched_video_count = 0
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
            matched_video_count += 1
        logger.info(
            f'GSC#{tournament.order} {level} 成绩录像读取完成，'
            f'匹配录像 {matched_video_count} 条',
        )

    for participant in participants:
        _apply_gsc_scores(participant, times_by_user_id.get(participant.user_id, {}))

    GSCParticipant.objects.bulk_update(participants, GSC_SCORE_FIELDS, batch_size=batch_size)

    logger.info(f'GSC#{tournament.order} 成绩刷新完成，更新参赛者 {len(participants)} 个')
    return len(participants)


def refresh_gsc_scores_and_ranks(tournament: GSCTournament):
    logger.info(f'GSC#{tournament.order} 成绩与排名刷新开始，比赛#{tournament.id}')
    score_changed = refresh_gsc_scores(tournament)
    rank_changed = refresh_tournament_ranks(tournament)
    result = {
        'score_changed': score_changed,
        'rank_changed': rank_changed,
    }
    logger.info(f'GSC#{tournament.order} 成绩与排名刷新完成，结果 {result}')
    return result


def update_gsc_best(tournament_user: TournamentUser, tournament: GSCTournament, participant: GSCParticipant):
    if participant.user_id is None or tournament.state != Tournament_TextChoices.State.AWARDED:
        return False

    new_best = gsc_encode_best(participant.t37, tournament.order)
    if tournament_user.gsc_best <= new_best:
        return False

    tournament_user.gsc_best = new_best
    return True


def get_gsc_scores(tournament: GSCTournament):
    return GSCParticipant.objects.filter(tournament=tournament)


def calculate_gsc_best_score(user_id: int):
    best_participant = (
        GSCParticipant.objects
        .filter(user_id=user_id, tournament__state=Tournament_TextChoices.State.AWARDED)
        .select_related('tournament__gsctournament')
        .order_by('t37', 'tournament__gsctournament__order')
        .first()
    )
    if best_participant is None:
        return MAX_TOURNAMENT_BEST
    return gsc_encode_best(best_participant.t37, best_participant.tournament.gsctournament.order)


def refresh_gsc_best_scores(tournament: GSCTournament, *, batch_size=1000):
    logger.info(f'GSC#{tournament.order} 个人纪录刷新 开始 类型{tournament.subclass}')
    logger.info(f'GSC#{tournament.order} 个人纪录刷新 获取选手列表')
    participants = list(
        GSCParticipant.objects
        .filter(tournament_id=tournament.id, user_id__isnull=False)
        .select_related('user__tournamentuser'),
    )
    logger.info(f'GSC#{tournament.order} 个人纪录刷新 人数 {len(participants)}')
    if not participants:
        logger.info(f'GSC#{tournament.order} 个人纪录刷新 结束')
        return 0

    tournament_users = []
    updated_count = 0
    for participant in participants:
        tournament_user = participant.user.tournamentuser
        updated_count += update_gsc_best(tournament_user, tournament, participant)
        tournament_users.append(tournament_user)

    TournamentUser.objects.bulk_update(tournament_users, ['gsc_best'], batch_size=batch_size)
    tournament_cache.update_tournament_users(tournament_users, fields=['gsc_best'])
    logger.info(f'GSC#{tournament.order} 个人纪录刷新 完成 人数{updated_count}')
    return updated_count
