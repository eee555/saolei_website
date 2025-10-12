from datetime import datetime, timezone
import logging

from django_redis import get_redis_connection
import ms_toollib as ms

from accountlink.models import AccountSaolei
from config.global_settings import GameLevels
from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from utils.getOldWebData import Level, VideoData
from .models import ExpandVideoModel, VideoModel

logger = logging.getLogger('videomanager')
cache = get_redis_connection("saolei_website")

video_all_fields = ["id", "upload_time", "player__id", "player__realname", "timems", "bv", "bvs", "state", "level", "mode", "software", "flag", "op", "isl", "path", "left", "right", "double", "left_ce", "right_ce",
                    "double_ce", "cell0", "cell1", "cell2", "cell3", "cell4", "cell5", "cell6", "cell7", "cell8", "left_s", "right_s", "double_s", "left_ces", "right_ces", "double_ces", "flag_s", "ioe", "thrp", "cl_s", "ce_s"]
for name in [field.name for field in ExpandVideoModel._meta.get_fields()]:
    video_all_fields.append("video__" + name)

# 状态到redis表名的映射
state2redis = {
    MS_TextChoices.State.PLAIN: 'review_queue',
    MS_TextChoices.State.FROZEN: 'freeze_queue',
    MS_TextChoices.State.IDENTIFIER: 'newest_queue',
    MS_TextChoices.State.OFFICIAL: 'newest_queue',
}


# 确定用户破某个纪录后，且对应模式、指标的三个级别全部有录像后，更新redis中的数据
def update_3_level_cache_record(realname: str, index: str, mode: str, ms_user: UserMS):
    key = f"player_{index}_{mode}_{ms_user.id}"
    cache.hset(key, "name", realname)
    for level in GameLevels:
        cache.hset(key, level, ms_user.getrecord(level, index, mode))
        recordid = ms_user.getrecordID(level, index, mode)
        cache.hset(key, f"{level}_id",
                   "None" if recordid is None else recordid)
    s = float(ms_user.getrecord("b", index, mode) + ms_user.getrecord("i",
              index, mode) + ms_user.getrecord("e", index, mode))
    cache.hset(key, "sum", s)
    cache.zadd(f"player_{index}_{mode}_ids", {ms_user.id: s})


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

    v.parse_video()
    v.analyse()
    v.current_time = 1e8

    if v.level == 3:
        video.level = 'b'
    elif v.level == 4:
        video.level = 'i'
    elif v.level == 5:
        video.level = 'e'
    elif v.level == 6:
        video.level = 'c'
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


def video_saolei_import_by_userid_helper(userProfile: UserProfile, accountSaolei: AccountSaolei, beginTime: datetime = datetime.min.replace(tzinfo=timezone.utc), endTime: datetime = datetime.max.replace(tzinfo=timezone.utc), is_need_file_url=False) -> VideoData.Info:

    def scheduleFunc(info: VideoData.Info) -> bool:
        videoModel = ExpandVideoModel.objects.create(
            identifier='',
            stnb=0,
        )
        videoModel.save()
        model = VideoModel.objects.create(
            player=userProfile,
            video=videoModel,
            state=MS_TextChoices.State.EXTERNAL,
            software='u',
            level=info.level[0].lower(),
            mode=(MS_TextChoices.Mode.STD, MS_TextChoices.Mode.NF)[info.mode],
            timems=info.grade * 1000,
            bv=info.bv,
            url_web=info.showUrl,
            url_file=info.url,
        )
        model.upload_time = info.dateTime
        model.save()
        return True
    urls = VideoModel.objects.filter(
        player=userProfile).values_list('url_web')
    url_set = {url for url, in urls}
    videodata = VideoData(accountSaolei.id, url_set, scheduleFunc)
    videodata.getData(Level.Beg, beginTime, endTime,
                      is_need_file_url)
    videodata.getData(Level.Int, beginTime, endTime,
                      is_need_file_url)
    videodata.getData(Level.Exp, beginTime, endTime,
                      is_need_file_url)
