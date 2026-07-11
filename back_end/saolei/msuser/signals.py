from typing import Any

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from utils import calculator
from videomanager.models import VideoModel
from .services import can_update_personal_record, decrement_video_count, get_current_record_keys_for_stats, increment_video_count, rebuild_personal_records, update_personal_record_stats
from .utils import RankingCategory, RankingField, VIDEO_RECORD_STATS, RankingStat, get_record_modes, get_video_num_limit, is_valid_ranking_level, is_valid_ranking_mode

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
            if getattr(userms, ranking_field.id_name) == video.id:
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
