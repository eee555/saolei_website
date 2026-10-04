from django.db.models import Min, QuerySet

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from videomanager.models import VideoModel
from .utils import get_video_num_limit


def increment_video_count(userms: UserMS, level: MS_TextChoices.Level, mode: MS_TextChoices.Mode, right_ce: int | None):
    """增加用户录像计数。"""
    userms.video_num_total += 1
    update_fields = ['video_num_total']
    if right_ce == 0:
        userms.video_num_nf += 1
        update_fields.append('video_num_nf')

    if mode == MS_TextChoices.Mode.STD:
        userms.video_num_std += 1
        update_fields.append('video_num_std')
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


def decrement_video_count(userms: UserMS, level: MS_TextChoices.Level, mode: MS_TextChoices.Mode, right_ce: int | None):
    """减少用户录像计数。"""
    userms.video_num_total -= 1
    update_fields = ['video_num_total']
    if right_ce == 0:
        userms.video_num_nf -= 1
        update_fields.append('video_num_nf')

    if mode == MS_TextChoices.Mode.STD:
        userms.video_num_std -= 1
        update_fields.append('video_num_std')
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


def update_video_count_limit_from_videos(userms: UserMS, videos: QuerySet[VideoModel]):
    """根据一批新转为官方的录像刷新用户录像数量上限。"""
    min_timems = (
        videos
        .filter(
            level=MS_TextChoices.Level.EXPERT,
            mode=MS_TextChoices.Mode.STD,
            state=MS_TextChoices.State.OFFICIAL,
        )
        .aggregate(min_timems=Min('timems'))['min_timems']
    )
    if min_timems is None:
        return

    video_num_limit = get_video_num_limit(min_timems)
    if video_num_limit > userms.video_num_limit:
        userms.video_num_limit = video_num_limit
        userms.save(update_fields=['video_num_limit'])
