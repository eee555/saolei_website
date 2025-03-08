import logging
from .models import VideoModel, ExpandVideoModel
from django_redis import get_redis_connection
from userprofile.models import UserProfile
from msuser.models import UserMS
import json
from utils import ComplexEncoder
from config.global_settings import RankingGameStats, GameLevels, GameModes, DefaultRankingScores
from utils.cmp import isbetter
from config.text_choices import MS_TextChoices
import ms_toollib as ms
from accountlink.models import AccountSaolei
from datetime import datetime, timezone
from utils.getOldWebData import VideoData, Level
from django.core.files import File
from identifier.utils import verify_identifier

logger = logging.getLogger('videomanager')
cache = get_redis_connection("saolei_website")

record_update_fields = []
for mode in GameModes:
    for stat in RankingGameStats:
        for level in GameLevels:
            record_update_fields.append(f"{level}_{stat}_{mode}")
            record_update_fields.append(f"{level}_{stat}_id_{mode}")

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


# 确定用户破某个纪录后，更新redis破纪录的记录，显示在首页用
def update_news_queue(user: UserProfile, ms_user: UserMS, video: VideoModel, index: str, mode: str):
    if ms_user.e_timems_std >= 60000 and (index != "timems" or video.level != "e"):
        return
    # print(f"{type(index)} {index}") # 调试用
    value = f"{getattr(video, index) / 1000:.3f}" if index == "timems" else f"{getattr(video, index):.3f}"
    delta_number = getattr(video, index) - \
        ms_user.getrecord(video.level, index, mode)
    if index == "timems":
        delta_number /= 1000
    # 看有没有存纪录录像的id，间接判断有没有纪录
    if ms_user.getrecordID(video.level, index, mode):
        delta = f"{delta_number:.3f}"
    else:
        delta = "新"
    cache.lpush("news_queue", json.dumps({"time": video.upload_time,
                                          "player": user.realname,
                                          "player_id": video.player.id,
                                          "video_id": video.id,
                                          "index": index,
                                          "mode": mode,
                                          "level": video.level,
                                          "value": value,
                                          "delta": delta}, cls=ComplexEncoder))


# 参数: 用户、拓展录像数据
# 增量式地更新用户的记录

# 检查用户是否可以加入排行，并更新排行榜
def checkRanking(userprof: UserProfile, user: UserMS, mode, statname):
    for level in GameLevels:
        if not isbetter(statname, user.getrecord(level, statname, mode), DefaultRankingScores[statname]):
            return
    update_3_level_cache_record(userprof.realname, statname, mode, user)


# 检查某录像是否打破个人纪录
def checkPB(video: VideoModel, user: UserMS, userprof: UserProfile, mode):
    for statname in RankingGameStats:
        stat = getattr(video, statname)
        if stat is not None and isbetter(statname, stat, user.getrecord(video.level, statname, mode)):
            update_news_queue(userprof, user, video, statname, mode)
            user.setrecord(video.level, statname, mode, stat)
            user.setrecordID(video.level, statname, mode, video.video.id)
            checkRanking(userprof, user, mode, statname)


def update_personal_record(video: VideoModel):
    if video.state != MS_TextChoices.State.OFFICIAL:
        return
    user = video.player
    ms_user = user.userms

    if video.mode == "12":
        video.mode = "00"
    if video.mode == "00":
        checkPB(video, ms_user, user, "std")

    if video.mode == "00":
        if video.flag == 0:
            video.mode = "12"

    if video.mode == "12":
        checkPB(video, ms_user, user, "nf")

    if video.mode == "05":
        checkPB(video, ms_user, user, "ng")

    if video.mode == "11":
        checkPB(video, ms_user, user, "dg")
    # 改完记录，存回数据库
    ms_user.save(update_fields=record_update_fields)


# 删除mysql中该用户所有的记录。删录像时用
def del_user_record_sql(user: UserProfile):
    ms_user: UserMS = user.userms
    for mode in GameModes:
        for stat in RankingGameStats:
            for level in GameLevels:
                ms_user.setrecord(level, stat, mode,
                                  DefaultRankingScores[stat])
                ms_user.setrecordID(level, stat, mode, None)
    ms_user.save(update_fields=record_update_fields)


# 删除redis中该用户所有的记录。删录像、删用户时用
def del_user_record_redis(user: UserProfile):
    ms_user: UserMS = user.userms
    _id = ms_user.id
    for mode in GameModes:
        for stat in RankingGameStats:
            cache.delete(f"player_{stat}_{mode}_{_id}")
            cache.zrem(f"player_{stat}_{mode}_ids", _id)


# 存量式更新用户的记录。删录像后用，恢复用户的记录。
def update_personal_record_stock(user: UserProfile):
    # e_video: ExpandVideoModel = video.video
    # user: UserProfile = video.player
    # ms_user: UserMS = user.userms
    del_user_record_sql(user)
    del_user_record_redis(user)
    videos = VideoModel.objects.filter(player=user)
    for v in videos:
        update_personal_record(v)


# 上传的录像进入数据库后，更新用户的录像数目
def update_video_num(video: VideoModel, add=True):
    userms = video.player.userms
    # add = True：新增录像；add = False：删除录像
    if video.mode == '00':
        userms.video_num_std += 1 if add else -1
    elif video.mode == '12':
        userms.video_num_nf += 1 if add else -1
    elif video.mode == '05':
        userms.video_num_ng += 1 if add else -1
    elif video.mode == '11':
        userms.video_num_dg += 1 if add else -1

    if video.level == "b":
        userms.video_num_beg += 1 if add else -1
    elif video.level == 'i':
        userms.video_num_int += 1 if add else -1
    elif video.level == 'e':
        userms.video_num_exp += 1 if add else -1

    if add:
        # 给高玩自动扩容
        if video.mode == "00" and video.level == 'e':
            if video.timems < 100000 and userms.video_num_limit < 200:
                userms.video_num_limit = 200
            if video.timems < 60000 and userms.video_num_limit < 500:
                userms.video_num_limit = 500
            if video.timems < 50000 and userms.video_num_limit < 600:
                userms.video_num_limit = 600
            if video.timems < 40000 and userms.video_num_limit < 800:
                userms.video_num_limit = 800
            if video.timems < 30000 and userms.video_num_limit < 1000:
                userms.video_num_limit = 1000

    userms.save(update_fields=["video_num_limit", "video_num_total", "video_num_beg", "video_num_int",
                "video_num_exp", "video_num_std", "video_num_nf", "video_num_ng", "video_num_dg"])


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
        update_personal_record(video)
    elif update_ranking and prevstate == MS_TextChoices.State.OFFICIAL:
        update_personal_record_stock(video)

def new_video_by_file(user: UserProfile, file: File):
    data = file.read()
    if file.name.endswith('.avf'):
        v = ms.AvfVideo(raw_data=data)
        software = 'a'
    elif file.name.endswith('.evf'):
        v = ms.EvfVideo(raw_data=data)
        software = 'e'
    elif file.name.endswith('.rmv'):
        v = ms.RmvVideo(raw_data=data)
        software = 'r'
    elif file.name.endswith('.mvf'):
        v = ms.MvfVideo(raw_data=data)
        software = 'm'
    else: 
        raise ValueError('不支持的文件类型')

    v.parse_video()
    v.analyse()
    v.current_time = 1e8

    if v.level == 3:
        level = 'b'
    elif v.level == 4:
        level = 'i'
    elif v.level == 5:
        level = 'e'
    else:
        raise ValueError('不支持的难度')
    
    review_code = v.is_valid()
    if review_code == 0:
        state = MS_TextChoices.State.OFFICIAL
    elif review_code == 1:
        state = MS_TextChoices.State.FROZEN
    elif review_code == 3:
        state = MS_TextChoices.State.PLAIN
    else:
        raise ValueError('无效的录像')

    if not user.userms:
        user.userms = UserMS.objects.create()

    identifier = bytes(v.player_identifier).decode('utf-8')
    if not verify_identifier(identifier):
        raise ValueError('无效的标识符')
    if identifier not in user.userms.identifiers and state == MS_TextChoices.State.OFFICIAL:
        state = MS_TextChoices.State.IDENTIFIER

    collisions = list(VideoModel.objects.filter(timems=v.rtime_ms, bv=v.bbbv).filter(path=v.path).filter(
        left=v.left, right=v.right, double=v.double, op=v.op, isl=v.isl))
    if collisions:
        raise ValueError('重复的录像')
    
    mode = str(v.mode).rjust(2, '0')
    if mode == '00' and v.flag == 0:
        mode = '12'

    e_video = ExpandVideoModel.objects.create(
        identifier=identifier,
        stnb=v.stnb,
        rqp=v.rqp,
    )
    video = VideoModel.objects.create(
        player=user,
        file=file,
        video=e_video,
        state=state,
        software=software,
        level=level,
        mode=mode,
        timems=v.rtime_ms,
        bv=v.bbbv,
        left=v.left,
        right=v.right,
        double=v.double,
        left_ce=v.lce,
        right_ce=v.rce,
        double_ce=v.dce,
        path=v.path,
        flag=v.flag,
        op=v.op,
        isl=v.isl,
        cell0=v.cell0,
        cell1=v.cell1,
        cell2=v.cell2,
        cell3=v.cell3,
        cell4=v.cell4,
        cell5=v.cell5,
        cell6=v.cell6,
        cell7=v.cell7,
        cell8=v.cell8,
    )

    if state == MS_TextChoices.State.PLAIN:
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 机审失败')
        video.push_redis("review_queue")
        update_video_num(video)
    elif state == MS_TextChoices.State.IDENTIFIER:
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 标识不匹配')
        video.push_redis("newest_queue")
        update_video_num(video)
    elif state == MS_TextChoices.State.FROZEN:
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 不合法')
        video.push_redis("freeze_queue")
    elif state == MS_TextChoices.State.OFFICIAL:  # 合法
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 机审成功')
        video.push_redis("newest_queue")
        update_personal_record(video)
        update_video_num(video)

    return video


def refresh_video(video: VideoModel):
    if video.file.path.endswith('.avf'):
        v = ms.AvfVideo(video.file.path)
        video.software = 'a'
    elif video.file.path.endswith('.evf'):
        v = ms.EvfVideo(video.file.path)
        video.software = 'e'
    else:
        return
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
    e_video.identifier = bytes(v.player_identifier).decode('utf-8')
    e_video.stnb = v.stnb
    e_video.rqp = v.rqp

    e_video.save()


def video_saolei_import_by_userid_helper(userProfile: UserProfile, accountSaolei: AccountSaolei, beginTime: datetime = datetime.min.replace(tzinfo=timezone.utc), endTime: datetime = datetime.max.replace(tzinfo=timezone.utc)) -> VideoData.Info:

    def scheduleFunc(info: VideoData.Info) -> bool:
        videoModel = ExpandVideoModel.objects.create(
            identifier='',
            stnb=0,
            rqp=0,
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
    videodata.getData(Level.Beg, beginTime, endTime)
    videodata.getData(Level.Int, beginTime, endTime)
    videodata.getData(Level.Exp, beginTime, endTime)
