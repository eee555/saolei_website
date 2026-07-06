import json

from django_redis import get_redis_connection

from config.global_settings import GameModes, RankingGameStats, record_update_fields
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from utils import ComplexEncoder
from utils.cmp import isbetter

cache = get_redis_connection('saolei_website')


def can_update_personal_record(video) -> bool:
    return (
        video.state == MS_TextChoices.State.OFFICIAL
        and not video.ongoing_tournament
        and video.player.userms_id is not None
    )


def update_news_queue(video, index: str, mode: str):
    """确定用户破某个纪录后，更新 Redis 破纪录消息。"""
    user = video.player
    ms_user = user.userms
    if ms_user.e_timems_std >= 60000 and (index != 'timems' or video.level != MS_TextChoices.Level.EXPERT):
        return
    value = f'{getattr(video, index) / 1000:.3f}' if index == 'timems' else f'{getattr(video, index):.3f}'
    delta_number = getattr(video, index) - ms_user.getrecord(video.level, index, mode)
    if index == 'timems':
        delta_number /= 1000
    if ms_user.getrecordID(video.level, index, mode):
        delta = f'{delta_number:.3f}'
    else:
        delta = '新'
    cache.lpush('news_queue', json.dumps({
        'time': video.upload_time,
        'player_id': user.id,
        'video_id': video.id,
        'index': index,
        'mode': mode,
        'level': video.level,
        'value': value,
        'delta': delta,
    }, cls=ComplexEncoder))


def check_personal_best(video, mode: str):
    """检查录像是否打破某个模式下的个人纪录。"""
    user = video.player
    userms = user.userms
    for statname in RankingGameStats:
        stat = getattr(video, statname)
        if stat is not None and isbetter(statname, stat, userms.getrecord(video.level, statname, mode)):
            update_news_queue(video, statname, mode)
            userms.setrecord(video.level, statname, mode, stat)
            userms.setrecordID(video.level, statname, mode, video.video_id)
            user.check_ms_ranking(statname, mode)


def update_personal_record(video):
    """增量式地更新录像玩家的经典个人纪录。"""
    if not can_update_personal_record(video):
        return

    if video.mode in {MS_TextChoices.Mode.NF, MS_TextChoices.Mode.STD}:
        check_personal_best(video, 'std')

    if video.mode == MS_TextChoices.Mode.NF:
        check_personal_best(video, 'nf')

    if video.mode == MS_TextChoices.Mode.JSW:
        check_personal_best(video, 'ng')

    if video.mode == MS_TextChoices.Mode.BZD:
        check_personal_best(video, 'dg')

    video.player.userms.save(update_fields=record_update_fields)


def update_personal_record_stock(user: UserProfile):
    """清空并用用户当前有效录像重算经典个人纪录。"""
    from videomanager.models import VideoModel

    user.userms.del_user_record_sql()
    user.userms.del_user_record_redis()
    videos = VideoModel.objects.filter(
        player=user,
        state=MS_TextChoices.State.OFFICIAL,
        ongoing_tournament=False,
    )
    for video in videos:
        update_personal_record(video)


def should_rebuild_personal_record(video, previous_video) -> bool:
    """判断已入榜录像发生修改时是否需要全量重算用户纪录。"""
    if previous_video is None or not can_update_personal_record(previous_video):
        return False

    record_id_fields = [
        f'{previous_video.level}_{stat}_id_{mode}'
        for mode in GameModes
        for stat in RankingGameStats
    ]
    if previous_video.video_id in {getattr(previous_video.player.userms, field) for field in record_id_fields}:
        return True

    for field in ['player_id', 'level', 'mode', 'timems', 'bv', 'bvs', 'stnb', 'ioe', 'path']:
        if getattr(previous_video, field) != getattr(video, field):
            return True

    return False
