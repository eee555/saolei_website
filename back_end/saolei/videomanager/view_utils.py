from .models import VideoModel, ExpandVideoModel
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from userprofile.models import UserProfile
from msuser.models import UserMS
import json
from utils import ComplexEncoder
from config.global_settings import *
from utils.cmp import isbetter
from django.db.models import F, ExpressionWrapper, DecimalField

record_update_fields = []
for mode in GameModes:
    for stat in RankingGameStats:
        for level in GameLevels:
            record_update_fields.append(f"{level}_{stat}_{mode}")
            record_update_fields.append(f"{level}_{stat}_id_{mode}")

# 确定用户破某个纪录后，且对应模式、指标的三个级别全部有录像后，更新redis中的数据
def update_3_level_cache_record(realname: str, index: str, mode: str, ms_user: UserMS):
    key = f"player_{index}_{mode}_{ms_user.id}"
    cache.hset(key, "name", realname)
    for level in GameLevels:
        cache.hset(key, level, ms_user.getrecord(level, index, mode))
        recordid = ms_user.getrecordID(level, index, mode)
        cache.hset(key, f"{level}_id", "None" if recordid is None else recordid)
    s = float(ms_user.getrecord("b", index, mode) + ms_user.getrecord("i", index, mode) +\
                ms_user.getrecord("e", index, mode))
    cache.hset(key, "sum", s)
    cache.zadd(f"player_{index}_{mode}_ids", {ms_user.id: s}) 


# 确定用户破某个纪录后，更新redis破纪录的记录，显示在首页用
def update_news_queue(user: UserProfile, ms_user: UserMS, video: VideoModel, index: str, mode: str):
    if ms_user.e_timems_std >= 60000 and (index != "timems" or video.level != "e"):
        return
    _video = video if index == "timems" or index == "bvs" else video.video
    # print(f"{type(index)} {index}") # 调试用
    value = f"{getattr(_video, index)/1000:.3f}" if index == "timems" else f"{getattr(_video, index):.3f}"
    delta_number = getattr(_video, index) - ms_user.getrecord(video.level, index, mode)
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
        if isbetter(statname, stat, user.getrecord(video.level, statname, mode)):
            update_news_queue(userprof, user, video, statname, mode)
            user.setrecord(video.level, statname, mode, stat)
            user.setrecordID(video.level, statname, mode, video.video.id)
            checkRanking(userprof, user, mode, statname)

def update_personal_record(video: VideoModel):
    e_video = video.video
    user = video.player
    ms_user = user.userms

    if video.mode == "12":
        video.mode = "00"
    if video.mode == "00":
        checkPB(video, ms_user, user, "std")

    if video.mode == "00":
        if e_video.flag == 0:
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

