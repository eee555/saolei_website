from datetime import datetime, timezone
import logging
import struct

from django_redis import get_redis_connection
import ms_toollib as ms

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.parser import pack_custom_level
from .models import ExpandVideoModel, VideoModel

logger = logging.getLogger('videomanager')
cache = get_redis_connection('saolei_website')

video_all_fields = [
    'id', 'upload_time', 'player__id', 'player__realname', 'timems', 'bv', 'bvs', 'state', 'level', 'mode', 'software', 'flag', 'op', 'isl', 'path', 'pluck', 'left', 'right', 'double', 'left_ce', 'right_ce',
    'double_ce', 'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8', 'left_s', 'right_s', 'double_s', 'left_ces', 'right_ces', 'double_ces', 'flag_s', 'ioe', 'thrp', 'cl_s', 'ce_s',
]
for name in [field.name for field in ExpandVideoModel._meta.get_fields()]:
    video_all_fields.append('video__' + name)

# 状态到redis表名的映射
state2redis = {
    MS_TextChoices.State.PLAIN: 'review_queue',
    MS_TextChoices.State.FROZEN: 'freeze_queue',
    MS_TextChoices.State.IDENTIFIER: 'newest_queue',
    MS_TextChoices.State.OFFICIAL: 'newest_queue',
}


# 存量式更新用户的记录。删录像后用，恢复用户的记录。
def update_personal_record_stock(user: UserProfile):
    # e_video: ExpandVideoModel = video.video
    # user: UserProfile = video.player
    # ms_user: UserMS = user.userms
    user.userms.del_user_record_sql()
    user.userms.del_user_record_redis()
    videos = VideoModel.objects.filter(player=user, ongoing_tournament=False)
    for v in videos:
        v.update_personal_record()


def update_state(video: VideoModel, state: MS_TextChoices.State, update_ranking=True):
    prevstate = video.state
    if prevstate == state:
        return
    video.pop_redis(state2redis[prevstate])
    video.state = state
    video.push_redis(state2redis[state])
    video.save()
    logger.info(f'录像#{video.id} 状态 从 {prevstate} 到 {state}')
    if state == MS_TextChoices.State.OFFICIAL:
        video.update_personal_record()
    elif update_ranking and prevstate == MS_TextChoices.State.OFFICIAL:
        update_personal_record_stock(video.player)
    from customranking.services import refresh_custom_pluck_rank_for_video
    from customranking.tasks import helper_custom_pluck
    if state == MS_TextChoices.State.OFFICIAL:
        helper_custom_pluck(video)
    elif prevstate == MS_TextChoices.State.OFFICIAL:
        refresh_custom_pluck_rank_for_video(video)


def refresh_video(video: VideoModel):
    if video.file.path.endswith('.avf'):
        v = ms.AvfVideo(video.file.path)
        video.software = 'a'
    elif video.file.path.endswith('.evf'):
        v = ms.EvfVideo(video.file.path)
        video.software = 'e'
    elif video.file.path.endswith('.rmv'):
        v = ms.RmvVideo(video.file.path)
        video.software = 'r'
    elif video.file.path.endswith('.mvf'):
        v = ms.MvfVideo(video.file.path)
        video.software = 'm'
    else:
        return

    video.file_size = video.file.size

    v.parse()
    v.analyse()
    v.current_time = 1e8

    if v.level == 3:
        video.level = 'b'
    elif v.level == 4:
        video.level = 'i'
    elif v.level == 5:
        video.level = 'e'
    elif v.level == 6:
        try:
            video.level = pack_custom_level(
                getattr(v, 'row', None),
                getattr(v, 'column', None),
                getattr(v, 'mine_num', None),
            )
        except ExceptionToResponse:
            return
    else:
        return

    video.end_time = datetime.fromtimestamp(v.end_time / 1000000, tz=timezone.utc)
    video.timems = v.rtime_ms
    video.bv = v.bbbv

    video.left = v.left
    video.right = v.right
    video.double = v.double

    video.left_ce = v.lce
    video.right_ce = v.rce
    video.double_ce = v.dce

    video.path = v.path
    video.pluck = None
    video.flag = v.flag
    video.op = v.op
    video.isl = v.isl

    video.cell0 = v.cell0
    video.cell1 = v.cell1
    video.cell2 = v.cell2
    video.cell3 = v.cell3
    video.cell4 = v.cell4
    video.cell5 = v.cell5
    video.cell6 = v.cell6
    video.cell7 = v.cell7
    video.cell8 = v.cell8

    video.save()

    e_video = video.video
    e_video.identifier = v.player_identifier
    e_video.stnb = v.stnb

    e_video.save()

    if video.state == MS_TextChoices.State.IDENTIFIER and (e_video.identifier in video.player.userms.identifiers):
        video.state = MS_TextChoices.State.OFFICIAL
        video.save()

    from customranking.tasks import helper_custom_pluck
    helper_custom_pluck(video)


def generate_file_stream(queryset):
    def file_iterator():
        for video in queryset:
            if not video.file:
                continue

            filename = f'{video.player.id}_{video.player.realname}/{video.file.name.split("/")[-1]}'
            filename_bytes = filename.encode('utf-8')
            filename_len = len(filename_bytes)
            filesize = video.file.size

            # Header: 4-byte filename length + filename + 8-byte file size
            yield struct.pack('>I', filename_len)
            yield filename_bytes
            yield struct.pack('>Q', filesize)  # unsigned long long, 8 bytes

            # File content
            with video.file.open('rb') as f:
                while chunk := f.read(8192):
                    yield chunk
    return file_iterator()
