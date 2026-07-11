from datetime import datetime, timedelta, timezone
import json
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_redis import get_redis_connection

from videomanager.models import VideoModel

logger = logging.getLogger(__name__)
cache = get_redis_connection('saolei_website')


# 定时任务文档
# https://pypi.org/project/django-apscheduler/
# def n_days_ago(obj, n=7) -> bool:
#     d = datetime.strptime(obj['time'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#     return (timezone.now().replace(tzinfo=timezone.utc) - d).days > n
def n_days_ago(time_str: str, n=7) -> bool:
    t = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - t
    return delta > timedelta(days=7)


# 定时清除最新录像，直至剩下最近7天的或剩下不到100条
@util.close_old_connections
def delete_newest_queue():
    if cache.hlen('newest_queue') <= 100:
        return
    newest_queue_ids = cache.hgetall('newest_queue')
    # newest_queue_ids的示例：
    # {b'1': b'{"time": "2024-05-22T17:31:06Z", "player": "\\u5b9e\\u540d", "player_id": 1,
    #  "level": "b", "mode": "00", "timems": 4770, "bv": 23, "bvs": 4.821802935010482}',
    # b'4': b'{"time": "2024-05-22T17:31:09Z", "player": "\\u5b9e\\u540d", "player_id": 1,
    # "level": "e", "mode": "00", "timems": 74710, "bv": 227, "bvs": 3.0384152054611167}'}
    for key in newest_queue_ids.keys():
        a = json.loads(newest_queue_ids[key])
        if n_days_ago(a['time']):
            cache.hdel('newest_queue', key)


# 定时清除7天以前冻结的录像
@util.close_old_connections
def delete_freezed_video():
    ddl = datetime.now(timezone.utc) - timedelta(days=7)
    VideoModel.objects.filter(upload_time__lt=ddl, state='b').delete()


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Runs APScheduler.'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            delete_newest_queue,
            trigger=CronTrigger(
                day_of_week='*', hour='01', minute='08',
            ),
            id='delete_newest_queue',
            misfire_grace_time=300,
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_newest_queue'.")

        scheduler.add_job(
            delete_freezed_video,
            trigger=CronTrigger(
                day_of_week='*', hour='01', minute='28',
            ),
            id='delete_freezed_video',
            misfire_grace_time=300,
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_freezed_video'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='03',
            ),  # Midnight on Monday, before start of the next work week.
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'.",
        )

        try:
            logger.info('Starting scheduler...')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Stopping scheduler...')
            scheduler.shutdown()
            logger.info('Scheduler shut down successfully!')
