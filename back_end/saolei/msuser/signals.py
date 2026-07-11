import json
from typing import Any

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_redis import get_redis_connection

from config.global_settings import DefaultRankingScores, GameLevels, GameModes, RankingGameStats
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from utils import ComplexEncoder, calculator
from videomanager.models import VideoModel
from .models import UserMS
from .services import can_update_personal_record, decrement_video_count, get_current_record_keys_for_stats, increment_video_count, rebuild_personal_records, update_personal_record_stats
from .utils import RankingCategory, RankingField, RankingValue, VIDEO_RECORD_STATS, RankingStat, get_record_modes, get_video_num_limit, is_valid_ranking_level, is_valid_ranking_mode

cache = get_redis_connection('saolei_website')

PERSONAL_RECORD_RELATED_VIDEO_FIELDS = {
    'state',
    'ongoing_tournament',
    'player',
    'player_id',
    'level',
    'mode',
    'timems',
    'upload_time',
    'bv',
    'left',
    'right',
    'double',
    'path',
}

NEWS_RECORD_FIELDS = {
    field
    for level in GameLevels
    for mode in GameModes
    for stat in RankingGameStats
    for field in (
        RankingField(level, stat, mode).name,
        RankingField(level, stat, mode).id_name,
    )
}
NEWS_QUEUE_MAX_SIZE = 200


@receiver(post_save, sender=VideoModel, dispatch_uid='msuser.update_video_count_on_video_save')
def update_video_count_on_video_save(sender, instance: VideoModel, created: bool, update_fields=None, **kwargs):
    if created and (userms := instance.player.userms) is not None:
        increment_video_count(userms, instance.level, instance.mode)


@receiver(post_save, sender=VideoModel, dispatch_uid='msuser.update_video_count_limit_on_video_save')
def update_video_count_limit_on_video_save(sender, instance: VideoModel, created: bool, update_fields=None, **kwargs):
    if instance.mode == MS_TextChoices.Mode.STD and instance.level == MS_TextChoices.Level.EXPERT and instance.state == MS_TextChoices.State.OFFICIAL:
        userms = instance.player.userms
        video_num_limit = get_video_num_limit(instance.timems)
        if video_num_limit > userms.video_num_limit:
            userms.video_num_limit = video_num_limit
            userms.save(update_fields=['video_num_limit'])


@receiver(post_delete, sender=VideoModel, dispatch_uid='msuser.update_video_count_on_video_delete')
def update_video_count_on_video_delete(sender, instance: VideoModel, **kwargs):
    if (userms := instance.player.userms) is not None:
        decrement_video_count(userms, instance.level, instance.mode)


@receiver(pre_save, sender=UserMS, dispatch_uid='msuser.capture_previous_records_for_news_queue')
def capture_previous_records_for_news_queue(sender, instance: UserMS, update_fields=None, **kwargs):
    if instance.pk is None or getattr(instance, '_skip_msuser_news_signal', False):
        instance._previous_news_records = {}
        return
    if update_fields is None:
        fields = NEWS_RECORD_FIELDS
    else:
        fields = set(update_fields) & NEWS_RECORD_FIELDS
    if not fields:
        instance._previous_news_records = {}
        return
    previous = UserMS.objects.filter(pk=instance.pk).values(*fields).first() or {}
    old_records = {}
    handled_fields = set()
    for field_name in previous:
        ranking_field = RankingField(field_name)
        if ranking_field in handled_fields or any(name not in previous for name in ranking_field.update_names):
            continue
        handled_fields.add(ranking_field)
        old_records[ranking_field] = RankingValue(previous[ranking_field.name], previous[ranking_field.id_name])
    instance._previous_news_records = old_records


def push_record_news(userms: UserMS, ranking_field: RankingField, old_record: RankingValue):
    current_record = userms.get_record(ranking_field)
    if current_record.video_id is None:
        return
    default_value = getattr(DefaultRankingScores, ranking_field.stat)
    old_value = None if old_record.value == default_value else old_record.value
    news_time = timezone.now()
    news = json.dumps({
        'time': news_time,
        'player_id': userms.parent.id,
        'video_id': current_record.video_id,
        'index': ranking_field.stat,
        'mode': ranking_field.mode,
        'level': ranking_field.level,
        'value': current_record.value,
        'old_value': old_value,
    }, cls=ComplexEncoder)
    cache.zadd('news_queue', {news: news_time.timestamp()})
    news_count = cache.zcard('news_queue')
    if news_count > NEWS_QUEUE_MAX_SIZE:
        cache.zremrangebyrank('news_queue', 0, news_count - NEWS_QUEUE_MAX_SIZE - 1)


@receiver(post_save, sender=UserMS, dispatch_uid='msuser.push_news_queue_on_record_save')
def push_news_queue_on_record_save(sender, instance: UserMS, created: bool, update_fields=None, **kwargs):
    if created or getattr(instance, '_skip_msuser_news_signal', False):
        return
    previous = getattr(instance, '_previous_news_records', {})
    if not previous:
        return
    for ranking_field, old_record in previous.items():
        if instance.get_record(ranking_field).value == old_record.value:
            continue
        push_record_news(instance, ranking_field, old_record)


def get_stats_update_set(video: VideoModel, old_values: dict[str, Any]) -> tuple[set[RankingStat], set[RankingStat]]:
    # better_upload_time
    if 'upload_time' in old_values:
        better_upload_time = calculator.cmp(
            old_values.get('upload_time').timestamp(),
            video.upload_time.timestamp(),
        )
    else:
        better_upload_time = 0

    # better_timems
    if 'timems' in old_values:
        better_timems = calculator.cmp(old_values.get('timems'), video.timems)
    else:
        better_timems = 0

    # better_path
    if 'path' in old_values:
        better_path = calculator.cmp(old_values.get('path'), video.path)
    else:
        better_path = 0

    # better_bvs
    if 'bv' in old_values or 'timems' in old_values:
        old_bv = old_values.get('bv', video.bv)
        old_timems = old_values.get('timems', video.timems)
        better_bvs = calculator.cmp(
            calculator.bvs(video.bv, video.timems),
            calculator.bvs(old_bv, old_timems),
        )
    else:
        better_bvs = 0

    # better_stnb
    if 'bv' in old_values or 'timems' in old_values:
        old_bv = old_values.get('bv', video.bv)
        old_timems = old_values.get('timems', video.timems)
        better_stnb = calculator.cmp(
            calculator.iqg(video.bv, video.timems),
            calculator.iqg(old_bv, old_timems),
        )
    else:
        better_stnb = 0

    # better_ioe
    if 'bv' in old_values or 'left' in old_values or 'right' in old_values or 'double' in old_values:
        old_bv = old_values.get('bv', video.bv)
        old_left = old_values.get('left', video.left)
        old_right = old_values.get('right', video.right)
        old_double = old_values.get('double', video.double)
        better_ioe = calculator.cmp(
            calculator.ioe(video.bv, video.left, video.right, video.double),
            calculator.ioe(old_bv, old_left, old_right, old_double),
        )
    else:
        better_ioe = 0

    better_stats: set[RankingStat] = set()
    worse_stats: set[RankingStat] = set()

    if better_timems > 0:
        better_stats.add('timems')
    elif better_timems < 0:
        worse_stats.add('timems')
    elif better_upload_time > 0:
        better_stats.add('timems')
    elif better_upload_time < 0:
        worse_stats.add('timems')

    if better_bvs > 0:
        better_stats.add('bvs')
    elif better_bvs < 0:
        worse_stats.add('bvs')
    elif better_bvs == 0:
        if 'timems' in better_stats:
            better_stats.add('bvs')
        elif 'timems' in worse_stats:
            worse_stats.add('bvs')

    if better_stnb > 0:
        better_stats.add('stnb')
    elif better_stnb < 0:
        worse_stats.add('stnb')
    elif better_stnb == 0:
        if 'timems' in better_stats:
            better_stats.add('stnb')
        elif 'timems' in worse_stats:
            worse_stats.add('stnb')

    if better_ioe > 0:
        better_stats.add('ioe')
    elif better_ioe < 0:
        worse_stats.add('ioe')
    elif better_ioe == 0:
        if 'timems' in better_stats:
            better_stats.add('ioe')
        elif 'timems' in worse_stats:
            worse_stats.add('ioe')

    if better_path > 0:
        better_stats.add('path')
    elif better_path < 0:
        worse_stats.add('path')
    elif better_path == 0:
        if 'timems' in better_stats:
            better_stats.add('path')
        elif 'timems' in worse_stats:
            worse_stats.add('path')

    return better_stats, worse_stats


def get_old_ranking_category(video: VideoModel, old_values: dict[str, Any]):
    if 'state' in old_values and old_values.get('state') != MS_TextChoices.State.OFFICIAL:
        return None
    if 'ongoing_tournament' in old_values and old_values.get('ongoing_tournament'):
        return None
    if not is_valid_ranking_level(old_level := old_values.get('level', video.level)):
        return None
    if not is_valid_ranking_mode(old_mode := old_values.get('mode', video.mode)):
        return None

    old_player_id: int = old_values.get('player_id', video.player_id)

    # 能进入经典排行的录像一定已有 UserMS；否则没有 identifiers，state 会停在 IDENTIFIER。
    return RankingCategory(old_player_id, old_level, old_mode)


def get_new_ranking_category(video: VideoModel):
    if video.state != MS_TextChoices.State.OFFICIAL:
        return None
    if video.ongoing_tournament:
        return None
    if not is_valid_ranking_level(video.level):
        return None
    if not is_valid_ranking_mode(video.mode):
        return None

    # 能进入经典排行的录像一定已有 UserMS；否则没有 identifiers，state 会停在 IDENTIFIER。
    return RankingCategory(video.player_id, video.level, video.mode)


def rebuild_records_for_category(video: VideoModel, category: RankingCategory, stats: set[RankingStat]):
    # TODO: 如果这里出现查询性能问题，可以改用 select_related('userms') 预取 UserMS。
    user = UserProfile.objects.get(id=category.player_id)
    userms = user.userms

    # 能进入经典排行的录像一定已有 UserMS；否则没有 identifiers，state 会停在 IDENTIFIER。
    record_keys: set[RankingField] = set()
    for record_mode in get_record_modes(category.mode):
        for stat in stats:
            ranking_field = RankingField(category.level, stat, record_mode)
            if userms.get_record(ranking_field).video_id == video.id:
                record_keys.add(ranking_field)
    rebuild_personal_records(user, record_keys)


@receiver(post_save, sender=VideoModel, dispatch_uid='msuser.refresh_personal_record_on_video_save')
def refresh_personal_record_on_video_save(sender, instance: VideoModel, created: bool, update_fields=None, **kwargs):
    if getattr(instance, '_skip_msuser_ranking_signal', False):
        return
    if update_fields is not None and not (set(update_fields) & PERSONAL_RECORD_RELATED_VIDEO_FIELDS):
        return

    old_ranking_category = get_old_ranking_category(instance, instance._old_values) if not created else None
    new_ranking_category = get_new_ranking_category(instance)

    if old_ranking_category is None and new_ranking_category is None:
        return

    instance.refresh_from_db(fields=['bvs', 'iqg', 'ioe'])

    if old_ranking_category == new_ranking_category:
        old_values: dict[str, Any] = getattr(instance, '_old_values', {})
        if created:
            better_stats = set(VIDEO_RECORD_STATS)
            worse_stats = set()
        else:
            better_stats, worse_stats = get_stats_update_set(instance, old_values)
        if better_stats:
            update_personal_record_stats(instance, better_stats)
        if worse_stats:
            rebuild_personal_records(instance.player, get_current_record_keys_for_stats(instance, worse_stats))
    else:
        if old_ranking_category is not None:
            rebuild_records_for_category(instance, old_ranking_category, set(VIDEO_RECORD_STATS))
        if new_ranking_category is not None:
            instance.player.userms.refresh_from_db()
            update_personal_record_stats(instance, VIDEO_RECORD_STATS)


@receiver(post_delete, sender=VideoModel, dispatch_uid='msuser.refresh_personal_record_on_video_delete')
def refresh_personal_record_on_video_delete(sender, instance: VideoModel, **kwargs):
    if not can_update_personal_record(instance):
        return
    rebuild_personal_records(instance.player, get_current_record_keys_for_stats(instance, set(VIDEO_RECORD_STATS)))
