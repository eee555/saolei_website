import logging

from django.db.models import F, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from tournament.models import TournamentUser, WeeklyParticipant, WeeklyTournament
from tournament.utils import MAX_TOURNAMENT_BEST
from .utils import weekly_encode_best

logger = logging.getLogger('tournament')


def refresh_weekly_classic_scores(tournament: WeeklyTournament, *, batch_size=1000):
    """
    批量刷新 周赛-2高5中 成绩。
    """
    logger.info(f'周赛#{tournament.id} classic 成绩刷新开始，{tournament.year}W{tournament.week}')
    participants = list(WeeklyParticipant.objects.filter(tournament=tournament))
    if not participants:
        logger.info(f'周赛#{tournament.id} classic 成绩刷新跳过，没有参赛者')
        return 0
    logger.info(f'周赛#{tournament.id} classic 成绩刷新参赛者读取完成，数量 {len(participants)}')

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
    expert_video_count = 0
    for video_id, player_id, timems in ranked_exp.iterator(chunk_size=batch_size):
        if player_id not in participants_by_user_id:
            continue
        participants_by_user_id[player_id].classic_add_e(video_id, timems)
        expert_video_count += 1
    logger.info(f'周赛#{tournament.id} classic 高级录像读取完成，匹配录像 {expert_video_count} 条')

    ranked_int = tournament.videos.filter(level=MS_TextChoices.Level.INTERMEDIATE, timems__lt=60000).annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F('player_id')],
            order_by='timems',
        ),
    ).filter(row_number__lte=5).values_list('id', 'player_id', 'timems')
    intermediate_video_count = 0
    for video_id, player_id, timems in ranked_int.iterator(chunk_size=batch_size):
        if player_id not in participants_by_user_id:
            continue
        participants_by_user_id[player_id].classic_add_i(video_id, timems)
        intermediate_video_count += 1
    logger.info(f'周赛#{tournament.id} classic 中级录像读取完成，匹配录像 {intermediate_video_count} 条')

    WeeklyParticipant.objects.bulk_update(participants, ['classic_et', 'classic_it', 'classic_score'], batch_size=batch_size)

    logger.info(f'周赛#{tournament.id} classic 成绩刷新完成，更新参赛者 {len(participants)} 个')
    return len(participants)


def update_weekly_best(tournament_user: TournamentUser, tournament: WeeklyTournament, participant: WeeklyParticipant):
    if participant.user_id is None or tournament.state != Tournament_TextChoices.State.AWARDED:
        return False

    new_best = weekly_encode_best(participant.classic_score, tournament.year, tournament.week)
    if tournament_user.weekly_classic_best <= new_best:
        return False

    tournament_user.weekly_classic_best = new_best
    return True


def calculate_weekly_classic_best(user_id: int):
    best_participant = (
        WeeklyParticipant.objects
        .filter(user_id=user_id, tournament__state=Tournament_TextChoices.State.AWARDED)
        .select_related('tournament__weeklytournament')
        .order_by('classic_score', 'tournament__weeklytournament__year', 'tournament__weeklytournament__week')
        .first()
    )
    if best_participant is None:
        return MAX_TOURNAMENT_BEST
    tournament = best_participant.tournament.weeklytournament
    return weekly_encode_best(best_participant.classic_score, tournament.year, tournament.week)


def refresh_weekly_best_scores(tournament: WeeklyTournament, *, batch_size=1000):
    logger.info(f'周赛#{tournament.id} 个人纪录刷新 开始 类型{tournament.subclass}')
    logger.info(f'周赛#{tournament.id} 个人纪录刷新 获取选手列表')
    participants = list(
        WeeklyParticipant.objects
        .filter(tournament_id=tournament.id, user_id__isnull=False)
        .select_related('user__tournamentuser'),
    )
    logger.info(f'周赛#{tournament.id} 个人纪录刷新 人数 {len(participants)}')
    if not participants:
        logger.info(f'周赛#{tournament.id} 个人纪录刷新 结束')
        return 0

    tournament_users = []
    updated_count = 0
    for participant in participants:
        tournament_user = participant.user.tournamentuser
        updated_count += update_weekly_best(tournament_user, tournament, participant)
        tournament_users.append(tournament_user)

    TournamentUser.objects.bulk_update(tournament_users, ['weekly_classic_best'], batch_size=batch_size)
    logger.info(f'周赛#{tournament.id} 个人纪录刷新 完成 人数{updated_count}')
    return updated_count
