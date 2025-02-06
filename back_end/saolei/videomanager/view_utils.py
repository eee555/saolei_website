import logging
from math import inf
from operator import le
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
import datetime
from utils.getOldWebData import VideoData,Level

logger = logging.getLogger('videomanager')
cache = get_redis_connection("saolei_website")

record_update_fields = []
for mode in GameModes:
    for stat in RankingGameStats:
        for level in GameLevels:
            record_update_fields.append(f"{level}_{stat}_{mode}")
            record_update_fields.append(f"{level}_{stat}_id_{mode}")

video_all_fields = ["id", "upload_time", "player__id", "player__realname", "timems", "bv", "bvs", "state", "level", "mode", "software", "flag", "op", "isl", "path", "left", "right", "double", "left_ce", "right_ce", "double_ce", "cell0", "cell1", "cell2", "cell3", "cell4", "cell5", "cell6", "cell7", "cell8", "left_s", "right_s", "double_s", "left_ces", "right_ces", "double_ces", "flag_s", "ioe", "thrp", "cl_s", "ce_s"]
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
        cache.hset(key, f"{level}_id", "None" if recordid is None else recordid)
    s = float(ms_user.getrecord("b", index, mode) + ms_user.getrecord("i", index, mode) + ms_user.getrecord("e", index, mode))
    cache.hset(key, "sum", s)
    cache.zadd(f"player_{index}_{mode}_ids", {ms_user.id: s})


# 确定用户破某个纪录后，更新redis破纪录的记录，显示在首页用
def update_news_queue(user: UserProfile, ms_user: UserMS, video: VideoModel, index: str, mode: str):
    if ms_user.e_timems_std >= 60000 and (index != "timems" or video.level != "e"):
        return
    # print(f"{type(index)} {index}") # 调试用
    value = f"{getattr(video, index) / 1000:.3f}" if index == "timems" else f"{getattr(video, index):.3f}"
    delta_number = getattr(video, index) - ms_user.getrecord(video.level, index, mode)
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
                ms_user.setrecord(level, stat, mode, DefaultRankingScores[stat])
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

    userms.save(update_fields=["video_num_limit", "video_num_total", "video_num_beg", "video_num_int", "video_num_exp", "video_num_std", "video_num_nf", "video_num_ng", "video_num_dg"])


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


def new_video(data, user):
    e_video = ExpandVideoModel.objects.create(
        identifier=data["identifier"],
        stnb=data["stnb"],
        rqp=data["rqp"],
    )
    video = VideoModel.objects.create(
        player=user,
        file=data["file"],
        video=e_video,
        state=["c", "b", "d", "a"][data['review_code']],
        software=data["software"],
        level=data["level"],
        mode=data["mode"] if data["mode"] != "00" else ("12" if data["flag"] == 0 else "00"),

        timems=data["timems"],
        bv=data["bv"],
        left=data["left"],
        right=data["right"],
        double=data["double"],
        left_ce=data["left_ce"],
        right_ce=data["right_ce"],
        double_ce=data["double_ce"],
        path=data["path"],
        flag=data["flag"],
        op=data["op"],
        isl=data["isl"],
        cell0=data["cell0"],
        cell1=data["cell1"],
        cell2=data["cell2"],
        cell3=data["cell3"],
        cell4=data["cell4"],
        cell5=data["cell5"],
        cell6=data["cell6"],
        cell7=data["cell7"],
        cell8=data["cell8"],
    )

    # 参考ms_toollib.is_valid的返回值
    if data['review_code'] == 3:  # 不确定
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 机审失败')
        video.push_redis("review_queue")
        update_video_num(video)
    elif data['review_code'] == 2:
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 标识不匹配')
        video.push_redis("newest_queue")
        update_video_num(video)
    elif data['review_code'] == 1:
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 不合法')
        video.push_redis("freeze_queue")
    elif data['review_code'] == 0:  # 合法
        logger.info(f'用户 {user.username}#{user.id} 录像#{video.id} 机审成功')
        video.push_redis("newest_queue")
        update_personal_record(video)
        update_video_num(video)


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
def video_saolei_import_by_userid_helper(userProfile:UserProfile,accountSaolei:AccountSaolei) -> VideoData.Info:
    infolast = None
    def scheduleFunc(info: VideoData.Info) -> bool:
        nonlocal infolast
        infolast = info
        video = ExpandVideoModel.objects.create(
                identifier='',
                stnb=0,
                rqp=0,
            )
        video.save()
        model = VideoModel.objects.create(
            player = userProfile,
            upload_time = datetime.datetime.strptime(info.dateTime,'%Y-%m-%d %H:%M:%S').astimezone(datetime.timezone.utc),
            video = video,
            state = MS_TextChoices.State.EXTERNAL,
            software = 'u',
            level = info.level[0].lower(),
            mode = (MS_TextChoices.Mode.STD,MS_TextChoices.Mode.NF)[info.mode],
            timems = info.grade * 1000,
            bv = info.bv,
            url_web = info.showUrl,
            url_file = info.url,
        )
        model.save()
        return True
    videodata = VideoData(accountSaolei.id,scheduleFunc)
    videodata.getData(Level.Beg,datetime.datetime.min)
    videodata.getData(Level.Int,datetime.datetime.min)
    videodata.getData(Level.Exp,datetime.datetime.min)
    return infolast