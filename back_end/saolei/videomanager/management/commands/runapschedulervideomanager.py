import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from django.utils import timezone
from datetime import datetime
import json
from videomanager.models import VideoModel, ExpandVideoModel

logger = logging.getLogger(__name__)

# 定时任务文档
# https://pypi.org/project/django-apscheduler/

def n_days_ago(obj, n=7) -> bool:
    d = datetime.strptime(obj['time'], "%Y-%m-%dT%H:%M:%SZ")
    return (timezone.now().replace(tzinfo=None) - d).days > n

# 定时清除最新录像，直至剩下最近7天的或剩下不到100条
def delete_newest_queue():
    if cache.hlen("newest_queue") <= 100:
        return
    newest_queue_ids = cache.hgetall("newest_queue")
    # newest_queue_ids的示例：
    # {b'1': b'{"time": "2024-05-22T17:31:06Z", "player": "\\u5b9e\\u540d", "player_id": 1,
    #  "level": "b", "mode": "00", "timems": 4770, "bv": 23, "bvs": 4.821802935010482}', 
    # b'4': b'{"time": "2024-05-22T17:31:09Z", "player": "\\u5b9e\\u540d", "player_id": 1, 
    # "level": "e", "mode": "00", "timems": 74710, "bv": 227, "bvs": 3.0384152054611167}'}
    for key in newest_queue_ids.keys():
        a = json.loads(newest_queue_ids[key])
        if n_days_ago(a):
            cache.hdel("newest_queue", key)


# 定时清除7天以前冻结的录像
def delete_freezed_video():
    ddl = timezone.now() - timezone.timedelta(days=7)
    VideoModel.objects.filter(upload_time__lt=ddl, state="b").delete()

# 定时清除新闻
def delete_news_queue():
    if cache.llen("news_queue") <= 100:
        return
    news_queue_list = cache.lrange("news_queue", 0, -1)
    # news_queue的示例：
    # [b'{"time": "2024-08-09T17:58:06Z", "player": "\\u7530\\u94ed\\u626c",
    #  "player_id": 5, "video_id": 6, "index": "timems", "mode": "std", 
    # "level": "e", "value": "54.760", "delta": "-8.130"}', b'{"time": 
    # "2024-08-09T17:48:38Z", "player": "\\u7530\\u94ed\\u626c", "player_id":
    #  5, "video_id": 5, "index": "timems", "mode": "nf", "level": "e", "value":
    #  "65.370", "delta": "\\u65b0"}']
    news_queue_list = [x for x in news_queue_list if not n_days_ago(json.loads(x))]
    cache.delete("news_queue")
    if news_queue_list:
        cache.rpush("news_queue", *news_queue_list)


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
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            delete_newest_queue,
            trigger=CronTrigger(
                day_of_week="*", hour="01", minute="08"
                ),
            id="delete_newest_queue",
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
            )
        logger.info("Added job 'delete_newest_queue'.")


        scheduler.add_job(
            delete_freezed_video,
            trigger=CronTrigger(
                day_of_week="*", hour="01", minute="13"
                ),
            id="delete_freezed_video",
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
            )
        logger.info("Added job 'delete_freezed_video'.")


        scheduler.add_job(
            delete_news_queue,
            trigger=CronTrigger(
                day_of_week="*", hour="17", minute="03"
                ),
            id="delete_news_queue",
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
            )
        logger.info("Added job 'delete_news_queue'.")


        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="03"
                ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
            )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
            )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")