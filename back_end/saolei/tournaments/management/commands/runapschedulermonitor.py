import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django_redis import get_redis_connection
from tournaments.models import Tournament
from config.text_choices import Tournament_TextChoices
from datetime import datetime


cache = get_redis_connection("saolei_website")
logger = logging.getLogger(__name__)

# 定时任务文档
# https://pypi.org/project/django-apscheduler/


# 5秒执行一次。定时计算刷新监视状态量。服务器io
def refresh_state_always():
    for tournament in Tournament.objects.filter(state=Tournament_TextChoices.State.PREPARING):
        if tournament.start_time < datetime.now():
            tournament.state = Tournament_TextChoices.State.ONGOING
        tournament.save()
    for tournament in Tournament.objects.filter(state=Tournament_TextChoices.State.ONGOING):
        if tournament.end_time < datetime.now():
            tournament.state = Tournament_TextChoices.State.FINISHED
            for video in tournament.videos:
                
        tournament.save()
    for tournament in Tournament.objects.filter(state=Tournament_TextChoices.State.PENDING):
        if tournament.start_time < datetime.now():
            tournament.state = Tournament_TextChoices.State.CANCELLED
        tournament.save()



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
        logger.setLevel(logging.ERROR)

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            refresh_state_always,
            trigger=CronTrigger(second="*/5"),  # Every 5 seconds
            id="refresh_state_always",  # The `id` assigned to each job MUST be unique
            misfire_grace_time=3,
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'refresh_state_always'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="03",
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'.",
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
