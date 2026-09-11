from datetime import datetime, timedelta, timezone
import json
import logging

from apscheduler.triggers.cron import CronTrigger
from captcha.models import CaptchaStore
from django.utils import timezone as django_timezone
from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution
from django_redis import get_redis_connection
import psutil

from userprofile.models import EmailVerifyRecord
from videomanager.models import VideoModel

logger = logging.getLogger(__name__)
cache = get_redis_connection('saolei_website')


@util.close_old_connections
def refresh_state_always():
    net_io = psutil.net_io_counters()
    net_io_sent_old = cache.get('io_s_old') if cache.exists('io_s_old') else '0.0'
    net_io_recv_old = cache.get('io_r_old') if cache.exists('io_r_old') else '0.0'
    cache.set('io_s_old', str(net_io.bytes_sent))
    cache.set('io_r_old', str(net_io.bytes_recv))
    io_s_spd = (net_io.bytes_sent - float(net_io_sent_old)) / 5
    io_r_spd = (net_io.bytes_recv - float(net_io_recv_old)) / 5
    cache.rpush('io_s_spds', str(io_s_spd))
    cache.rpush('io_r_spds', str(io_r_spd))
    if cache.llen('io_s_spds') > 120:
        cache.lpop('io_s_spds')
    if cache.llen('io_r_spds') > 120:
        cache.lpop('io_r_spds')

    cpu = psutil.cpu_percent()
    cache.rpush('cpus', str(cpu))
    if cache.llen('cpus') > 120:
        cache.lpop('cpus')


@util.close_old_connections
def delete_overdue_emailverifyrecord():
    start = django_timezone.now() - django_timezone.timedelta(seconds=3600)
    EmailVerifyRecord.objects.filter(send_time__lt=start).delete()


@util.close_old_connections
def delete_overdue_captcha():
    CaptchaStore.objects.filter(expiration__lt=django_timezone.now()).delete()


def n_days_ago(time_str: str, n=7) -> bool:
    t = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - t
    return delta > timedelta(days=n)


@util.close_old_connections
def delete_newest_queue():
    if cache.hlen('newest_queue') <= 100:
        return
    newest_queue_ids = cache.hgetall('newest_queue')
    for key in newest_queue_ids.keys():
        video_info = json.loads(newest_queue_ids[key])
        if n_days_ago(video_info['time']):
            cache.hdel('newest_queue', key)


@util.close_old_connections
def delete_freezed_video():
    ddl = datetime.now(timezone.utc) - timedelta(days=7)
    VideoModel.objects.filter(upload_time__lt=ddl, state='b').delete()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def register_jobs(scheduler):
    scheduler.add_job(
        refresh_state_always,
        trigger=CronTrigger(second='*/5'),
        id='refresh_state_always',
        misfire_grace_time=3,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'refresh_state_always'.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week='mon', hour='00', minute='03'),
        id='delete_old_job_executions',
        misfire_grace_time=30,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    scheduler.add_job(
        delete_newest_queue,
        trigger=CronTrigger(day_of_week='*', hour='01', minute='08'),
        id='delete_newest_queue',
        misfire_grace_time=300,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'delete_newest_queue'.")

    scheduler.add_job(
        delete_freezed_video,
        trigger=CronTrigger(day_of_week='*', hour='01', minute='28'),
        id='delete_freezed_video',
        misfire_grace_time=300,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'delete_freezed_video'.")

    scheduler.add_job(
        delete_overdue_emailverifyrecord,
        trigger=CronTrigger(day_of_week='mon', hour='01', minute='03'),
        id='delete_overdue_emailverifyrecord',
        misfire_grace_time=30,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'delete_overdue_emailverifyrecord'.")

    scheduler.add_job(
        delete_overdue_captcha,
        trigger=CronTrigger(day_of_week='mon', hour='01', minute='05'),
        id='delete_overdue_captcha',
        misfire_grace_time=30,
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'delete_overdue_captcha'.")
