from .models import VideoModel, ExpandVideoModel
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from userprofile.models import UserProfile
from msuser.models import UserMS


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
    cache.hset(key, "b", _float(getattr(ms_user, f"b_{index}_{mode}")))
    cache.hset(key, "b_id", getattr(ms_user, f"b_{index}_id_{mode}"))
    cache.hset(key, "i", _float(getattr(ms_user, f"i_{index}_{mode}")))
    cache.hset(key, "i_id", getattr(ms_user, f"i_{index}_id_{mode}"))
    cache.hset(key, "e", _float(getattr(ms_user, f"e_{index}_{mode}")))
    cache.hset(key, "e_id", getattr(ms_user, f"e_{index}_id_{mode}"))
    s = _float(getattr(ms_user, f"b_{index}_{mode}") + getattr(ms_user, f"i_{index}_{mode}") +\
                getattr(ms_user, f"e_{index}_{mode}"))
    cache.hset(key, "sum", s)
    cache.zadd(f"player_{index}_{mode}_ids", {ms_user.id: s}) 



# 参数: 用户、拓展录像数据
# 增量式地更新用户的记录
def update_personal_record(video: VideoModel):
    e_video = video.video
    user = video.player
    ms_user = user.userms

    if video.mode == "12":
        video.mode = "00"
    if video.mode == "00":
        if video.level == "b":
            if video.rtime < ms_user.b_time_std:
                ms_user.b_time_std = video.rtime
                ms_user.b_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    update_3_level_cache_record(user.realname, "time", "std", ms_user)
            if video.bvs > ms_user.b_bvs_std:
                ms_user.b_bvs_std = video.bvs
                ms_user.b_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "std", ms_user)
            if e_video.stnb > ms_user.b_stnb_std:
                ms_user.b_stnb_std = e_video.stnb
                ms_user.b_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "std", ms_user)
            if e_video.ioe > ms_user.b_ioe_std:
                ms_user.b_ioe_std = e_video.ioe
                ms_user.b_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "std", ms_user)
            if e_video.path < ms_user.b_path_std:
                ms_user.b_path_std = e_video.path
                ms_user.b_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "std", ms_user)
        if video.level == "i":
            if video.rtime < ms_user.i_time_std:
                ms_user.i_time_std = video.rtime
                ms_user.i_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    update_3_level_cache_record(user.realname, "time", "std", ms_user)
            if video.bvs > ms_user.i_bvs_std:
                ms_user.i_bvs_std = video.bvs
                ms_user.i_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "std", ms_user)
            if e_video.stnb > ms_user.i_stnb_std:
                ms_user.i_stnb_std = e_video.stnb
                ms_user.i_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "std", ms_user)
            if e_video.ioe > ms_user.i_ioe_std:
                ms_user.i_ioe_std = e_video.ioe
                ms_user.i_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "std", ms_user)
            if e_video.path < ms_user.i_path_std:
                ms_user.i_path_std = e_video.path
                ms_user.i_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "std", ms_user)
        if video.level == "e":
            if video.rtime < ms_user.e_time_std:
                ms_user.e_time_std = video.rtime
                ms_user.e_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    update_3_level_cache_record(user.realname, "time", "std", ms_user)
            if video.bvs > ms_user.e_bvs_std:
                ms_user.e_bvs_std = video.bvs
                ms_user.e_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "std", ms_user)
            if e_video.stnb > ms_user.e_stnb_std:
                ms_user.e_stnb_std = e_video.stnb
                ms_user.e_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "std", ms_user)
            if e_video.ioe > ms_user.e_ioe_std:
                ms_user.e_ioe_std = e_video.ioe
                ms_user.e_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "std", ms_user)
            if e_video.path < ms_user.e_path_std:
                ms_user.e_path_std = e_video.path
                ms_user.e_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "std", ms_user)

    if video.mode == "00":
        if e_video.flag == 0:
            video.mode = "12"

    if video.mode == "12":
        if video.level == "b":
            if video.rtime < ms_user.b_time_nf:
                ms_user.b_time_nf = video.rtime
                ms_user.b_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    update_3_level_cache_record(user.realname, "time", "nf", ms_user)
            if video.bvs > ms_user.b_bvs_nf:
                ms_user.b_bvs_nf = video.bvs
                ms_user.b_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "nf", ms_user)
            if e_video.stnb > ms_user.b_stnb_nf:
                ms_user.b_stnb_nf = e_video.stnb
                ms_user.b_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "nf", ms_user)
            if e_video.ioe > ms_user.b_ioe_nf:
                ms_user.b_ioe_nf = e_video.ioe
                ms_user.b_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "nf", ms_user)
            if e_video.path < ms_user.b_path_nf:
                ms_user.b_path_nf = e_video.path
                ms_user.b_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "nf", ms_user)
        if video.level == "i":
            if video.rtime < ms_user.i_time_nf:
                ms_user.i_time_nf = video.rtime
                ms_user.i_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    update_3_level_cache_record(user.realname, "time", "nf", ms_user)
            if video.bvs > ms_user.i_bvs_nf:
                ms_user.i_bvs_nf = video.bvs
                ms_user.i_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "nf", ms_user)
            if e_video.stnb > ms_user.i_stnb_nf:
                ms_user.i_stnb_nf = e_video.stnb
                ms_user.i_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "nf", ms_user)
            if e_video.ioe > ms_user.i_ioe_nf:
                ms_user.i_ioe_nf = e_video.ioe
                ms_user.i_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "nf", ms_user)
            if e_video.path < ms_user.i_path_nf:
                ms_user.i_path_nf = e_video.path
                ms_user.i_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "nf", ms_user)
        if video.level == "e":
            if video.rtime < ms_user.e_time_nf:
                ms_user.e_time_nf = video.rtime
                ms_user.e_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    update_3_level_cache_record(user.realname, "time", "nf", ms_user)
            if video.bvs > ms_user.e_bvs_nf:
                ms_user.e_bvs_nf = video.bvs
                ms_user.e_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "nf", ms_user)
            if e_video.stnb > ms_user.e_stnb_nf:
                ms_user.e_stnb_nf = e_video.stnb
                ms_user.e_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "nf", ms_user)
            if e_video.ioe > ms_user.e_ioe_nf:
                ms_user.e_ioe_nf = e_video.ioe
                ms_user.e_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "nf", ms_user)
            if e_video.path < ms_user.e_path_nf:
                ms_user.e_path_nf = e_video.path
                ms_user.e_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "nf", ms_user)

    if video.mode == "05":
        if video.level == "b":
            if video.rtime < ms_user.b_time_ng:
                ms_user.b_time_ng = video.rtime
                ms_user.b_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    update_3_level_cache_record(user.realname, "time", "ng", ms_user)
            if video.bvs > ms_user.b_bvs_ng:
                ms_user.b_bvs_ng = video.bvs
                ms_user.b_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "ng", ms_user)
            if e_video.stnb > ms_user.b_stnb_ng:
                ms_user.b_stnb_ng = e_video.stnb
                ms_user.b_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "ng", ms_user)
            if e_video.ioe > ms_user.b_ioe_ng:
                ms_user.b_ioe_ng = e_video.ioe
                ms_user.b_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "ng", ms_user)
            if e_video.path < ms_user.b_path_ng:
                ms_user.b_path_ng = e_video.path
                ms_user.b_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "ng", ms_user)
        if video.level == "i":
            if video.rtime < ms_user.i_time_ng:
                ms_user.i_time_ng = video.rtime
                ms_user.i_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    update_3_level_cache_record(user.realname, "time", "ng", ms_user)
            if video.bvs > ms_user.i_bvs_ng:
                ms_user.i_bvs_ng = video.bvs
                ms_user.i_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "ng", ms_user)
            if e_video.stnb > ms_user.i_stnb_ng:
                ms_user.i_stnb_ng = e_video.stnb
                ms_user.i_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "ng", ms_user)
            if e_video.ioe > ms_user.i_ioe_ng:
                ms_user.i_ioe_ng = e_video.ioe
                ms_user.i_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "ng", ms_user)
            if e_video.path < ms_user.i_path_ng:
                ms_user.i_path_ng = e_video.path
                ms_user.i_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "ng", ms_user)
        if video.level == "e":
            if video.rtime < ms_user.e_time_ng:
                ms_user.e_time_ng = video.rtime
                ms_user.e_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    update_3_level_cache_record(user.realname, "time", "ng", ms_user)
            if video.bvs > ms_user.e_bvs_ng:
                ms_user.e_bvs_ng = video.bvs
                ms_user.e_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "ng", ms_user)
            if e_video.stnb > ms_user.e_stnb_ng:
                ms_user.e_stnb_ng = e_video.stnb
                ms_user.e_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "ng", ms_user)
            if e_video.ioe > ms_user.e_ioe_ng:
                ms_user.e_ioe_ng = e_video.ioe
                ms_user.e_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "ng", ms_user)
            if e_video.path < ms_user.e_path_ng:
                ms_user.e_path_ng = e_video.path
                ms_user.e_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "ng", ms_user)

    if video.mode == "11":
        if video.level == "b":
            if video.rtime < ms_user.b_time_dg:
                ms_user.b_time_dg = video.rtime
                ms_user.b_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    update_3_level_cache_record(user.realname, "time", "dg", ms_user)
            if video.bvs > ms_user.b_bvs_dg:
                ms_user.b_bvs_dg = video.bvs
                ms_user.b_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "dg", ms_user)
            if e_video.stnb > ms_user.b_stnb_dg:
                ms_user.b_stnb_dg = e_video.stnb
                ms_user.b_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "dg", ms_user)
            if e_video.ioe > ms_user.b_ioe_dg:
                ms_user.b_ioe_dg = e_video.ioe
                ms_user.b_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "dg", ms_user)
            if e_video.path < ms_user.b_path_dg:
                ms_user.b_path_dg = e_video.path
                ms_user.b_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "dg", ms_user)
        if video.level == "i":
            if video.rtime < ms_user.i_time_dg:
                ms_user.i_time_dg = video.rtime
                ms_user.i_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    update_3_level_cache_record(user.realname, "time", "dg", ms_user)
            if video.bvs > ms_user.i_bvs_dg:
                ms_user.i_bvs_dg = video.bvs
                ms_user.i_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "dg", ms_user)
            if e_video.stnb > ms_user.i_stnb_dg:
                ms_user.i_stnb_dg = e_video.stnb
                ms_user.i_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "dg", ms_user)
            if e_video.ioe > ms_user.i_ioe_dg:
                ms_user.i_ioe_dg = e_video.ioe
                ms_user.i_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "dg", ms_user)
            if e_video.path < ms_user.i_path_dg:
                ms_user.i_path_dg = e_video.path
                ms_user.i_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "dg", ms_user)
        if video.level == "e":
            if video.rtime < ms_user.e_time_dg:
                ms_user.e_time_dg = video.rtime
                ms_user.e_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    update_3_level_cache_record(user.realname, "time", "dg", ms_user)
            if video.bvs > ms_user.e_bvs_dg:
                ms_user.e_bvs_dg = video.bvs
                ms_user.e_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    update_3_level_cache_record(user.realname, "bvs", "dg", ms_user)
            if e_video.stnb > ms_user.e_stnb_dg:
                ms_user.e_stnb_dg = e_video.stnb
                ms_user.e_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    update_3_level_cache_record(user.realname, "stnb", "dg", ms_user)
            if e_video.ioe > ms_user.e_ioe_dg:
                ms_user.e_ioe_dg = e_video.ioe
                ms_user.e_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    update_3_level_cache_record(user.realname, "ioe", "dg", ms_user)
            if e_video.path < ms_user.e_path_dg:
                ms_user.e_path_dg = e_video.path
                ms_user.e_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    update_3_level_cache_record(user.realname, "path", "dg", ms_user)
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
    cache.delete(f"player_time_std_{_id}")
    cache.delete(f"player_bvs_std_{_id}")
    cache.delete(f"player_stnb_std_{_id}")
    cache.delete(f"player_ioe_std_{_id}")
    cache.delete(f"player_path_std_{_id}")

    cache.delete(f"player_time_nf_{_id}")
    cache.delete(f"player_bvs_nf_{_id}")
    cache.delete(f"player_stnb_nf_{_id}")
    cache.delete(f"player_ioe_nf_{_id}")
    cache.delete(f"player_path_nf_{_id}")
    
    cache.delete(f"player_time_ng_{_id}")
    cache.delete(f"player_bvs_ng_{_id}")
    cache.delete(f"player_stnb_ng_{_id}")
    cache.delete(f"player_ioe_ng_{_id}")
    cache.delete(f"player_path_ng_{_id}")
    
    cache.delete(f"player_time_dg_{_id}")
    cache.delete(f"player_bvs_dg_{_id}")
    cache.delete(f"player_stnb_dg_{_id}")
    cache.delete(f"player_ioe_dg_{_id}")
    cache.delete(f"player_path_dg_{_id}")

    cache.zrem("player_time_std_ids", _id)
    cache.zrem("player_bvs_std_ids", _id)
    cache.zrem("player_stnb_std_ids", _id)
    cache.zrem("player_ioe_std_ids", _id)
    cache.zrem("player_path_std_ids", _id)

    cache.zrem("player_time_nf_ids", _id)
    cache.zrem("player_bvs_nf_ids", _id)
    cache.zrem("player_stnb_nf_ids", _id)
    cache.zrem("player_ioe_nf_ids", _id)
    cache.zrem("player_path_nf_ids", _id)

    cache.zrem("player_time_ng_ids", _id)
    cache.zrem("player_bvs_ng_ids", _id)
    cache.zrem("player_stnb_ng_ids", _id)
    cache.zrem("player_ioe_ng_ids", _id)
    cache.zrem("player_path_ng_ids", _id)
    
    cache.zrem("player_time_dg_ids", _id)
    cache.zrem("player_bvs_dg_ids", _id)
    cache.zrem("player_stnb_dg_ids", _id)
    cache.zrem("player_ioe_dg_ids", _id)
    cache.zrem("player_path_dg_ids", _id)


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



