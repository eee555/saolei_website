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

import psutil

logger = logging.getLogger(__name__)

# 定时任务文档
# https://pypi.org/project/django-apscheduler/


# 5秒执行一次。定时计算刷新监视状态量。服务器io
def refresh_state_always():
    net_io = psutil.net_io_counters()
    net_io_sent_old = cache.get("io_s_old") if cache.exists("io_s_old") else "0.0"
    net_io_recv_old = cache.get("io_r_old") if cache.exists("io_r_old") else "0.0"
    cache.set("io_s_old", str(net_io.bytes_sent))
    cache.set("io_r_old", str(net_io.bytes_recv))
    io_s_spd = (net_io.bytes_sent - float(net_io_sent_old)) / 5
    io_r_spd = (net_io.bytes_recv - float(net_io_recv_old)) / 5
    # print(io_s_spd)
    # print(io_r_spd)
    # cache.set("io_s_spd", str((net_io.bytes_sent - float(net_io_sent_old)) / 5))
    # cache.set("io_r_spd", str((net_io.bytes_recv - float(net_io_recv_old)) / 5))
    cache.rpush("io_s_spds", str(io_s_spd))
    cache.rpush("io_r_spds", str(io_r_spd))
    if cache.llen("io_s_spds") > 120:
        cache.lpop("io_s_spds")
    if cache.llen("io_r_spds") > 120:
        cache.lpop("io_r_spds")

    cpu = psutil.cpu_percent()
    # cache.set("cpu", str(cpu))
    cache.rpush("cpus", str(cpu))
    if cache.llen("cpus") > 120:
        cache.lpop("cpus")



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
            refresh_state_always,
            trigger=CronTrigger(second="*/5"),  # Every 5 seconds
            id="refresh_state_always",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
            )
        logger.info("Added job 'refresh_state_always'.")

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