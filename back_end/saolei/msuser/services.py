from typing import Iterable

from config.global_settings import DefaultRankingScores, GameLevels, GameModes, RankingGameStats
from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from utils.cmp import isbetter
from videomanager.models import VideoModel
from .utils import RankingField, RankingMode, RankingStat, RankingValue, get_record_modes, is_valid_ranking_level, is_valid_ranking_mode

STOCK_RECORD_QUERY_FIELDS = {
    'timems': 'timems',
    'bvs': 'bvs',
    'stnb': 'iqg',
    'ioe': 'ioe',
    'path': 'path',
}


def can_update_personal_record(video: VideoModel) -> bool:
    return (
        video.state == MS_TextChoices.State.OFFICIAL
        and is_valid_ranking_level(video.level)
        and is_valid_ranking_mode(video.mode)
        and not video.ongoing_tournament
    )


def increment_video_count(userms: UserMS, level: MS_TextChoices.Level, mode: MS_TextChoices.Mode):
    """增加用户录像计数。"""
    userms.video_num_total += 1
    update_fields = ['video_num_total']

    if mode == MS_TextChoices.Mode.STD:
        userms.video_num_std += 1
        update_fields.append('video_num_std')
    elif mode == MS_TextChoices.Mode.NF:
        userms.video_num_nf += 1
        update_fields.append('video_num_nf')
    elif mode == MS_TextChoices.Mode.JSW:
        userms.video_num_ng += 1
        update_fields.append('video_num_ng')
    elif mode == MS_TextChoices.Mode.BZD:
        userms.video_num_dg += 1
        update_fields.append('video_num_dg')

    if level == MS_TextChoices.Level.BEGINNER:
        userms.video_num_beg += 1
        update_fields.append('video_num_beg')
    elif level == MS_TextChoices.Level.INTERMEDIATE:
        userms.video_num_int += 1
        update_fields.append('video_num_int')
    elif level == MS_TextChoices.Level.EXPERT:
        userms.video_num_exp += 1
        update_fields.append('video_num_exp')

    userms.save(update_fields=update_fields)


def decrement_video_count(userms: UserMS, level: MS_TextChoices.Level, mode: MS_TextChoices.Mode):
    """减少用户录像计数。"""
    userms.video_num_total -= 1
    update_fields = ['video_num_total']

    if mode == MS_TextChoices.Mode.STD:
        userms.video_num_std -= 1
        update_fields.append('video_num_std')
    elif mode == MS_TextChoices.Mode.NF:
        userms.video_num_nf -= 1
        update_fields.append('video_num_nf')
    elif mode == MS_TextChoices.Mode.JSW:
        userms.video_num_ng -= 1
        update_fields.append('video_num_ng')
    elif mode == MS_TextChoices.Mode.BZD:
        userms.video_num_dg -= 1
        update_fields.append('video_num_dg')

    if level == MS_TextChoices.Level.BEGINNER:
        userms.video_num_beg -= 1
        update_fields.append('video_num_beg')
    elif level == MS_TextChoices.Level.INTERMEDIATE:
        userms.video_num_int -= 1
        update_fields.append('video_num_int')
    elif level == MS_TextChoices.Level.EXPERT:
        userms.video_num_exp -= 1
        update_fields.append('video_num_exp')

    userms.save(update_fields=update_fields)


def check_personal_best_stats(video: VideoModel, userms: UserMS, mode: RankingMode, stats: Iterable[RankingStat]):
    """检查录像是否打破某个模式下的指定个人纪录。"""
    update_fields = []
    for statname in stats:
        stat = getattr(video, statname)
        ranking_field = RankingField(video.level, statname, mode)
        if stat is not None and isbetter(statname, stat, userms.get_record(ranking_field).value):
            userms.set_record(ranking_field, RankingValue(stat, video.id))
            update_fields.extend(ranking_field.update_names)
            video.player.check_ms_ranking(statname, mode)
    return update_fields


def update_personal_record_stats(video: VideoModel, stats: list[RankingStat] | set[RankingStat] | tuple[RankingStat, ...]):
    """增量式地更新录像玩家的指定经典个人纪录。"""
    if not stats or not can_update_personal_record(video):
        return

    userms = video.player.userms
    update_fields = []
    for mode in get_record_modes(video.mode):
        update_fields.extend(check_personal_best_stats(video, userms, mode, stats))

    if update_fields:
        userms.save(update_fields=list(dict.fromkeys(update_fields)))


def get_current_record_keys_for_stats(video: VideoModel, stats: set[RankingStat]):
    if not stats or not is_valid_ranking_level(video.level) or not is_valid_ranking_mode(video.mode):
        return set[RankingField]()
    record_keys = set[RankingField]()
    userms = video.player.userms
    for stat in stats:
        for mode in get_record_modes(video.mode):
            ranking_field = RankingField(video.level, stat, mode)
            if userms.get_record(ranking_field).video_id == video.id:
                record_keys.add(ranking_field)
    return record_keys


def get_best_video_for_field(user: UserProfile, field: RankingField):
    from videomanager.models import VideoModel

    videos = VideoModel.objects.filter(
        player=user,
        level=field.level,
        state=MS_TextChoices.State.OFFICIAL,
        ongoing_tournament=False,
    )

    if field.mode == 'std':
        videos = videos.filter(mode__in=[MS_TextChoices.Mode.STD, MS_TextChoices.Mode.NF])
    elif field.mode == 'nf':
        videos = videos.filter(mode=MS_TextChoices.Mode.NF)
    elif field.mode == 'ng':
        videos = videos.filter(mode=MS_TextChoices.Mode.JSW)
    elif field.mode == 'dg':
        videos = videos.filter(mode=MS_TextChoices.Mode.BZD)
    else:
        return None

    query_field = STOCK_RECORD_QUERY_FIELDS[field.stat]
    if field.stat in {'timems', 'path'}:
        order_by = [query_field, 'timems', 'upload_time']
    else:
        order_by = [f'-{query_field}', 'timems', 'upload_time']
    return videos.exclude(**{f'{query_field}__isnull': True}).order_by(*order_by).first()


def rebuild_personal_records(user: UserProfile, record_keys: set[RankingField]):
    """只重算指定的经典个人纪录。"""
    if not record_keys:
        return

    userms = user.userms
    update_fields = []
    cache_keys = set()

    for ranking_field in record_keys:
        video = get_best_video_for_field(user, ranking_field)
        if video is None:
            userms.set_record(ranking_field, RankingValue(getattr(DefaultRankingScores, ranking_field.stat), None))
        else:
            userms.set_record(ranking_field, RankingValue(getattr(video, ranking_field.stat), video.id))
        update_fields.extend(ranking_field.update_names)
        cache_keys.add((ranking_field.stat, ranking_field.mode))

    userms._skip_msuser_news_signal = True
    try:
        userms.save(update_fields=update_fields)
    finally:
        userms._skip_msuser_news_signal = False
    for stat, mode in cache_keys:
        userms.update_3_level_cache_record(stat, mode)


def update_personal_record_stock(user: UserProfile):
    """清空并用用户当前有效录像重算经典个人纪录。"""
    user.userms.del_user_record_redis()
    rebuild_personal_records(
        user,
        {
            RankingField(level, stat, mode)
            for mode in GameModes
            for stat in RankingGameStats
            for level in GameLevels
        },
    )
