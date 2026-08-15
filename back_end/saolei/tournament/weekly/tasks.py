import logging

from django.tasks import task
from django_tasks import TaskResultStatus

from config.text_choices import Tournament_TextChoices
from tournament.models import WeeklyTournament
from tournament.services import create_tournament_users_for_tournament, delete_participants_without_videos, reveal_videos_for_tournament
from tournament.tasks import task_award_tournament
from .services import refresh_weekly_best_scores, refresh_weekly_classic_ranks, refresh_weekly_classic_scores

logger = logging.getLogger('tournament')


def helper_weekly_finish_tournament(tournament: WeeklyTournament):
    existing_task = tournament.task
    if existing_task:
        if existing_task.status == TaskResultStatus.SUCCESSFUL:
            logger.info(
                f'周赛#{tournament.id} 删除已完成的旧结算任务，'
                f'任务#{tournament.task_id}',
            )
            existing_task.delete()
        elif existing_task.status in [TaskResultStatus.READY, TaskResultStatus.RUNNING]:
            logger.info(
                f'周赛#{tournament.id} 复用进行中的结算任务，'
                f'任务#{tournament.task_id}，状态 {existing_task.status}',
            )
            return existing_task

    tournament.task = task_weekly_finish.enqueue(tournament.id).db_result
    tournament.save(update_fields=['task'])
    logger.info(
        f'周赛#{tournament.id} 创建结算任务完成，任务#{tournament.task_id}，'
        f'状态 {tournament.task.status}',
    )
    return tournament.task


def _task_weekly_finish_impl(tournament_id: int):
    logger.info(f'周赛#{tournament_id} 结算任务开始')
    tournament = WeeklyTournament.objects.get(id=tournament_id)
    try:
        logger.info(
            f'周赛#{tournament.id} 结算开始，{tournament.year}W{tournament.week}，'
            f'当前状态 {tournament.state}',
        )
        deleted_participants = delete_participants_without_videos(tournament)
        logger.info(f'周赛#{tournament.id} 删除无录像参赛者完成，数量 {deleted_participants}')
        tournament_users = create_tournament_users_for_tournament(tournament)
        logger.info(f'周赛#{tournament.id} TournamentUser 准备完成，数量 {len(tournament_users)}')
        score_count = refresh_weekly_classic_scores(tournament)
        logger.info(f'周赛#{tournament.id} 成绩刷新完成，数量 {score_count}')
        rank_count = refresh_weekly_classic_ranks(tournament)
        logger.info(f'周赛#{tournament.id} 排名刷新完成，数量 {rank_count}')
        if tournament.state != Tournament_TextChoices.State.AWARDED:
            tournament.state = Tournament_TextChoices.State.AWARDED
            tournament.save(update_fields=['state'])
            logger.info(f'周赛#{tournament.id} 状态已切换为 AWARDED')
        else:
            logger.info(f'周赛#{tournament.id} 状态已是 AWARDED，跳过状态切换')
        video_count = reveal_videos_for_tournament(tournament)
        logger.info(f'周赛#{tournament.id} 录像公开完成，数量 {video_count}')
        result = {
            'tournament_users': len(tournament_users),
            'deleted_participants': deleted_participants,
            'score_count': score_count,
            'rank_count': rank_count,
            'video_count': video_count,
        }
        logger.info(f'周赛#{tournament.id} 结算完成，结果 {result}')
    except Exception:
        logger.exception(f'周赛#{tournament_id} 结算任务失败')
        raise
    logger.info(f'周赛#{tournament_id} 结算任务完成，结果 {result}')
    task_award_tournament.enqueue(tournament.id)
    task_weekly_refresh_best.enqueue(tournament_id)
    return result


@task
def task_weekly_finish(tournament_id: int):
    return _task_weekly_finish_impl(tournament_id)


def _task_weekly_refresh_best_impl(tournament_id: int):
    tournament = WeeklyTournament.objects.get(id=tournament_id)
    tournament_users = create_tournament_users_for_tournament(tournament)
    return refresh_weekly_best_scores(tournament, tournament_users=tournament_users)


@task
def task_weekly_refresh_best(tournament_id: int):
    return _task_weekly_refresh_best_impl(tournament_id)
