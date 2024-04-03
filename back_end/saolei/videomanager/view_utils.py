from .models import VideoModel, ExpandVideoModel
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from userprofile.models import UserProfile
from msuser.models import UserMS
import json
from utils import ComplexEncoder
from config.global_settings import *
from utils.cmp import isbetter

record_update_fields=["b_time_std", "b_time_id_std", "i_time_std", "i_time_id_std", 
                      "e_time_std", "e_time_id_std", "b_bvs_std", "b_bvs_id_std", 
                      "i_bvs_std", "i_bvs_id_std", "e_bvs_std", "e_bvs_id_std", 
                      "b_stnb_std", "b_stnb_id_std", "i_stnb_std", "i_stnb_id_std", 
                      "e_stnb_std", "e_stnb_id_std", "b_ioe_std", "b_ioe_id_std", 
                      "i_ioe_std", "i_ioe_id_std", "e_ioe_std", "e_ioe_id_std", 
                      "b_path_std", "b_path_id_std", "i_path_std", "i_path_id_std",
                      "e_path_std", "e_path_id_std",
                      "b_time_nf", "b_time_id_nf", "i_time_nf", "i_time_id_nf", 
                      "e_time_nf", "e_time_id_nf", "b_bvs_nf", "b_bvs_id_nf", 
                      "i_bvs_nf", "i_bvs_id_nf", "e_bvs_nf", "e_bvs_id_nf", 
                      "b_stnb_nf", "b_stnb_id_nf", "i_stnb_nf", "i_stnb_id_nf", 
                      "e_stnb_nf", "e_stnb_id_nf", "b_ioe_nf", "b_ioe_id_nf", 
                      "i_ioe_nf", "i_ioe_id_nf", "e_ioe_nf", "e_ioe_id_nf", 
                      "b_path_nf", "b_path_id_nf", "i_path_nf", "i_path_id_nf",
                      "e_path_nf", "e_path_id_nf",
                      "b_time_ng", "b_time_id_ng", "i_time_ng", "i_time_id_ng", 
                      "e_time_ng", "e_time_id_ng", "b_bvs_ng", "b_bvs_id_ng", 
                      "i_bvs_ng", "i_bvs_id_ng", "e_bvs_ng", "e_bvs_id_ng", 
                      "b_stnb_ng", "b_stnb_id_ng", "i_stnb_ng", "i_stnb_id_ng", 
                      "e_stnb_ng", "e_stnb_id_ng", "b_ioe_ng", "b_ioe_id_ng", 
                      "i_ioe_ng", "i_ioe_id_ng", "e_ioe_ng", "e_ioe_id_ng", 
                      "b_path_ng", "b_path_id_ng", "i_path_ng", "i_path_id_ng",
                      "e_path_ng", "e_path_id_ng",
                      "b_time_dg", "b_time_id_dg", "i_time_dg", "i_time_id_dg", 
                      "e_time_dg", "e_time_id_dg", "b_bvs_dg", "b_bvs_id_dg", 
                      "i_bvs_dg", "i_bvs_id_dg", "e_bvs_dg", "e_bvs_id_dg", 
                      "b_stnb_dg", "b_stnb_id_dg", "i_stnb_dg", "i_stnb_id_dg", 
                      "e_stnb_dg", "e_stnb_id_dg", "b_ioe_dg", "b_ioe_id_dg", 
                      "i_ioe_dg", "i_ioe_id_dg", "e_ioe_dg", "e_ioe_id_dg", 
                      "b_path_dg", "b_path_id_dg", "i_path_dg", "i_path_id_dg",
                      "e_path_dg", "e_path_id_dg"]


# 确定用户破某个纪录后，且对应模式、指标的三个级别全部有录像后，更新redis中的数据
def update_3_level_cache_record(realname: str, index: str, mode: str, ms_user: UserMS):
    _float = float if index == "time" else lambda x: x
    key = f"player_{index}_{mode}_{ms_user.id}"
    cache.hset(key, "name", realname)
    for level in GameLevels:
        cache.hset(key, level, _float(ms_user.getrecord(level, index, mode)))
        cache.hset(key, f"{level}_id", _float(ms_user.getrecordID(level, index, mode)))
    s = _float(ms_user.getrecord("b", index, mode) + ms_user.getrecord("i", index, mode) +\
                ms_user.getrecord("e", index, mode))
    cache.hset(key, "sum", s)
    cache.zadd(f"player_{index}_{mode}_ids", {ms_user.id: s}) 


# 确定用户破某个纪录后，更新redis破纪录的记录，显示在首页用
def update_news_queue(user: UserProfile, ms_user: UserMS, video: VideoModel, index: str, mode: str):
    if float(ms_user.e_time_std) >= 60 and (index != "time" or video.level != "e"):
        return
    _video = video if index == "time" or index == "bvs" else video.video
    # print(f"{type(index)} {index}") # 调试用
    value = f"{getattr(_video, index):.3f}"
    delta_number = getattr(_video, index) - ms_user.getrecord(video.level, index, mode)
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
    ms_user.b_time_std = 999.999
    ms_user.b_time_id_std = None
    ms_user.i_time_std = 999.999
    ms_user.i_time_id_std = None
    ms_user.e_time_std = 999.999
    ms_user.e_time_id_std = None
    ms_user.b_bvs_std = 0.0
    ms_user.b_bvs_id_std = None
    ms_user.i_bvs_std = 0.0
    ms_user.i_bvs_id_std = None
    ms_user.e_bvs_std = 0.0
    ms_user.e_bvs_id_std = None
    ms_user.b_stnb_std = 0.0
    ms_user.b_stnb_id_std = None
    ms_user.i_stnb_std = 0.0
    ms_user.i_stnb_id_std = None
    ms_user.e_stnb_std = 0.0
    ms_user.e_stnb_id_std = None
    ms_user.b_ioe_std = 0.0
    ms_user.b_ioe_id_std = None
    ms_user.i_ioe_std = 0.0
    ms_user.i_ioe_id_std = None
    ms_user.e_ioe_std = 0.0
    ms_user.e_ioe_id_std = None
    ms_user.b_path_std = 99999.9
    ms_user.b_path_id_std = None
    ms_user.i_path_std = 99999.9
    ms_user.i_path_id_std = None
    ms_user.e_path_std = 99999.9
    ms_user.e_path_id_std = None

    ms_user.b_time_nf = 999.999
    ms_user.b_time_id_nf = None
    ms_user.i_time_nf = 999.999
    ms_user.i_time_id_nf = None
    ms_user.e_time_nf = 999.999
    ms_user.e_time_id_nf = None
    ms_user.b_bvs_nf = 0.0
    ms_user.b_bvs_id_nf = None
    ms_user.i_bvs_nf = 0.0
    ms_user.i_bvs_id_nf = None
    ms_user.e_bvs_nf = 0.0
    ms_user.e_bvs_id_nf = None
    ms_user.b_stnb_nf = 0.0
    ms_user.b_stnb_id_nf = None
    ms_user.i_stnb_nf = 0.0
    ms_user.i_stnb_id_nf = None
    ms_user.e_stnb_nf = 0.0
    ms_user.e_stnb_id_nf = None
    ms_user.b_ioe_nf = 0.0
    ms_user.b_ioe_id_nf = None
    ms_user.i_ioe_nf = 0.0
    ms_user.i_ioe_id_nf = None
    ms_user.e_ioe_nf = 0.0
    ms_user.e_ioe_id_nf = None
    ms_user.b_path_nf = 99999.9
    ms_user.b_path_id_nf = None
    ms_user.i_path_nf = 99999.9
    ms_user.i_path_id_nf = None
    ms_user.e_path_nf = 99999.9
    ms_user.e_path_id_nf = None

    ms_user.b_time_ng = 999.999
    ms_user.b_time_id_ng = None
    ms_user.i_time_ng = 999.999
    ms_user.i_time_id_ng = None
    ms_user.e_time_ng = 999.999
    ms_user.e_time_id_ng = None
    ms_user.b_bvs_ng = 0.0
    ms_user.b_bvs_id_ng = None
    ms_user.i_bvs_ng = 0.0
    ms_user.i_bvs_id_ng = None
    ms_user.e_bvs_ng = 0.0
    ms_user.e_bvs_id_ng = None
    ms_user.b_stnb_ng = 0.0
    ms_user.b_stnb_id_ng = None
    ms_user.i_stnb_ng = 0.0
    ms_user.i_stnb_id_ng = None
    ms_user.e_stnb_ng = 0.0
    ms_user.e_stnb_id_ng = None
    ms_user.b_ioe_ng = 0.0
    ms_user.b_ioe_id_ng = None
    ms_user.i_ioe_ng = 0.0
    ms_user.i_ioe_id_ng = None
    ms_user.e_ioe_ng = 0.0
    ms_user.e_ioe_id_ng = None
    ms_user.b_path_ng = 99999.9
    ms_user.b_path_id_ng = None
    ms_user.i_path_ng = 99999.9
    ms_user.i_path_id_ng = None
    ms_user.e_path_ng = 99999.9
    ms_user.e_path_id_ng = None

    ms_user.b_time_dg = 999.999
    ms_user.b_time_id_dg = None
    ms_user.i_time_dg = 999.999
    ms_user.i_time_id_dg = None
    ms_user.e_time_dg = 999.999
    ms_user.e_time_id_dg = None
    ms_user.b_bvs_dg = 0.0
    ms_user.b_bvs_id_dg = None
    ms_user.i_bvs_dg = 0.0
    ms_user.i_bvs_id_dg = None
    ms_user.e_bvs_dg = 0.0
    ms_user.e_bvs_id_dg = None
    ms_user.b_stnb_dg = 0.0
    ms_user.b_stnb_id_dg = None
    ms_user.i_stnb_dg = 0.0
    ms_user.i_stnb_id_dg = None
    ms_user.e_stnb_dg = 0.0
    ms_user.e_stnb_id_dg = None
    ms_user.b_ioe_dg = 0.0
    ms_user.b_ioe_id_dg = None
    ms_user.i_ioe_dg = 0.0
    ms_user.i_ioe_id_dg = None
    ms_user.e_ioe_dg = 0.0
    ms_user.e_ioe_id_dg = None
    ms_user.b_path_dg = 99999.9
    ms_user.b_path_id_dg = None
    ms_user.i_path_dg = 99999.9
    ms_user.i_path_id_dg = None
    ms_user.e_path_dg = 99999.9
    ms_user.e_path_id_dg = None

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



