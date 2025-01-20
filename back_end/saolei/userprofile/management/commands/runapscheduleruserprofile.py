import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.utils import timezone
from userprofile.models import EmailVerifyRecord
from captcha.models import CaptchaStore


logger = logging.getLogger(__name__)

# 定时任务文档
# https://pypi.org/project/django-apscheduler/


def delete_overdue_emailverifyrecord():
    # 定时清除过期邮箱验证码（1小时过期）
    start = timezone.now() - timezone.timedelta(seconds=3600)
    EmailVerifyRecord.objects.filter(send_time__lt=start).delete()


def delete_overdue_captcha():
    # 定时清除过期图形验证码（15分钟过期）
    # start = timezone.now() - timezone.timedelta(seconds=900)
    CaptchaStore.objects.filter(expiration__lt=timezone.now()).delete()


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
            delete_overdue_emailverifyrecord,
            trigger=CronTrigger(
                day_of_week="mon", hour="01", minute="03"
            ),
            id="delete_overdue_emailverifyrecord",  # The `id` assigned to each job MUST be unique
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_overdue_emailverifyrecord'.")

        scheduler.add_job(
            delete_overdue_captcha,
            trigger=CronTrigger(
                day_of_week="mon", hour="01", minute="05"
            ),
            id="delete_overdue_captcha",  # The `id` assigned to each job MUST be unique
            misfire_grace_time=30,
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_overdue_captcha'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="03"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            misfire_grace_time=30,
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
