from django.db import models

from django_redis import get_redis_connection
from config.global_settings import GameLevels, DefaultRankingScores, record_update_fields, GameModes, RankingGameStats

cache = get_redis_connection("saolei_website")


def get_default_identifiers():
    return []


def RTimeField():  # 以毫秒计数
    return models.PositiveIntegerField(default=DefaultRankingScores["timems"])


def BBBVsField():
    return models.FloatField(default=DefaultRankingScores["bvs"])


def STNBField():
    return models.FloatField(default=DefaultRankingScores["stnb"])


def IOEField():
    return models.FloatField(default=DefaultRankingScores["ioe"])


def PathField():
    return models.FloatField(default=DefaultRankingScores["path"])


def VideoIDField():
    return models.BigIntegerField(null=True)


def VideoCountField():
    return models.IntegerField(null=False, default=0)


# 扫雷用户的标识、记录、录像计数
# 此处目前太大，拆成多个模型或app比较好
class UserMS(models.Model):
    # 用户的标识。管理员审核通过后可以自由使用该标识。
    identifiers = models.JSONField(default=get_default_identifiers)
    # 总录像数限制默认100，计划管理员可以修改。高水平玩家也可以增多。
    # 高级标准sub100是200；sub60是500；sub50是600；sub40是800；sub30是1000；vip是1000。
    video_num_limit = models.IntegerField(null=False, default=100)

    # 录像计数
    video_num_total = VideoCountField()  # 录像总数
    video_num_beg = VideoCountField()  # 初级
    video_num_int = VideoCountField()  # 中级
    video_num_exp = VideoCountField()  # 高级
    video_num_std = VideoCountField()  # 标准
    video_num_nf = VideoCountField()  # 盲扫
    video_num_ng = VideoCountField()  # 无猜
    video_num_dg = VideoCountField()  # 递归

    # 标准、盲扫、无猜、递归的记录
    b_timems_std = RTimeField()
    b_timems_id_std = VideoIDField()
    i_timems_std = RTimeField()
    i_timems_id_std = VideoIDField()
    e_timems_std = RTimeField()
    e_timems_id_std = VideoIDField()
    b_bvs_std = BBBVsField()
    b_bvs_id_std = VideoIDField()
    i_bvs_std = BBBVsField()
    i_bvs_id_std = VideoIDField()
    e_bvs_std = BBBVsField()
    e_bvs_id_std = VideoIDField()
    b_stnb_std = STNBField()
    b_stnb_id_std = VideoIDField()
    i_stnb_std = STNBField()
    i_stnb_id_std = VideoIDField()
    e_stnb_std = STNBField()
    e_stnb_id_std = VideoIDField()
    b_ioe_std = IOEField()
    b_ioe_id_std = VideoIDField()
    i_ioe_std = IOEField()
    i_ioe_id_std = VideoIDField()
    e_ioe_std = IOEField()
    e_ioe_id_std = VideoIDField()
    b_path_std = PathField()
    b_path_id_std = VideoIDField()
    i_path_std = PathField()
    i_path_id_std = VideoIDField()
    e_path_std = PathField()
    e_path_id_std = VideoIDField()

    b_timems_nf = RTimeField()
    b_timems_id_nf = VideoIDField()
    i_timems_nf = RTimeField()
    i_timems_id_nf = VideoIDField()
    e_timems_nf = RTimeField()
    e_timems_id_nf = VideoIDField()
    b_bvs_nf = BBBVsField()
    b_bvs_id_nf = VideoIDField()
    i_bvs_nf = BBBVsField()
    i_bvs_id_nf = VideoIDField()
    e_bvs_nf = BBBVsField()
    e_bvs_id_nf = VideoIDField()
    b_stnb_nf = STNBField()
    b_stnb_id_nf = VideoIDField()
    i_stnb_nf = STNBField()
    i_stnb_id_nf = VideoIDField()
    e_stnb_nf = STNBField()
    e_stnb_id_nf = VideoIDField()
    b_ioe_nf = IOEField()
    b_ioe_id_nf = VideoIDField()
    i_ioe_nf = IOEField()
    i_ioe_id_nf = VideoIDField()
    e_ioe_nf = IOEField()
    e_ioe_id_nf = VideoIDField()
    b_path_nf = PathField()
    b_path_id_nf = VideoIDField()
    i_path_nf = PathField()
    i_path_id_nf = VideoIDField()
    e_path_nf = PathField()
    e_path_id_nf = VideoIDField()

    b_timems_ng = RTimeField()
    b_timems_id_ng = VideoIDField()
    i_timems_ng = RTimeField()
    i_timems_id_ng = VideoIDField()
    e_timems_ng = RTimeField()
    e_timems_id_ng = VideoIDField()
    b_bvs_ng = BBBVsField()
    b_bvs_id_ng = VideoIDField()
    i_bvs_ng = BBBVsField()
    i_bvs_id_ng = VideoIDField()
    e_bvs_ng = BBBVsField()
    e_bvs_id_ng = VideoIDField()
    b_stnb_ng = STNBField()
    b_stnb_id_ng = VideoIDField()
    i_stnb_ng = STNBField()
    i_stnb_id_ng = VideoIDField()
    e_stnb_ng = STNBField()
    e_stnb_id_ng = VideoIDField()
    b_ioe_ng = IOEField()
    b_ioe_id_ng = VideoIDField()
    i_ioe_ng = IOEField()
    i_ioe_id_ng = VideoIDField()
    e_ioe_ng = IOEField()
    e_ioe_id_ng = VideoIDField()
    b_path_ng = PathField()
    b_path_id_ng = VideoIDField()
    i_path_ng = PathField()
    i_path_id_ng = VideoIDField()
    e_path_ng = PathField()
    e_path_id_ng = VideoIDField()

    b_timems_dg = RTimeField()
    b_timems_id_dg = VideoIDField()
    i_timems_dg = RTimeField()
    i_timems_id_dg = VideoIDField()
    e_timems_dg = RTimeField()
    e_timems_id_dg = VideoIDField()
    b_bvs_dg = BBBVsField()
    b_bvs_id_dg = VideoIDField()
    i_bvs_dg = BBBVsField()
    i_bvs_id_dg = VideoIDField()
    e_bvs_dg = BBBVsField()
    e_bvs_id_dg = VideoIDField()
    b_stnb_dg = STNBField()
    b_stnb_id_dg = VideoIDField()
    i_stnb_dg = STNBField()
    i_stnb_id_dg = VideoIDField()
    e_stnb_dg = STNBField()
    e_stnb_id_dg = VideoIDField()
    b_ioe_dg = IOEField()
    b_ioe_id_dg = VideoIDField()
    i_ioe_dg = IOEField()
    i_ioe_id_dg = VideoIDField()
    e_ioe_dg = IOEField()
    e_ioe_id_dg = VideoIDField()
    b_path_dg = PathField()
    b_path_id_dg = VideoIDField()
    i_path_dg = PathField()
    i_path_id_dg = VideoIDField()
    e_path_dg = PathField()
    e_path_id_dg = VideoIDField()

    def __str__(self):
        return 'identifiers: {}'.format(self.identifiers)

    def getrecord(self, level, stat, mode):
        return getattr(self, f"{level}_{stat}_{mode}")

    def getrecordID(self, level, stat, mode):
        return getattr(self, f"{level}_{stat}_id_{mode}")

    def setrecord(self, level, stat, mode, score):
        setattr(self, f"{level}_{stat}_{mode}", score)

    def setrecordID(self, level, stat, mode, recordid):
        setattr(self, f"{level}_{stat}_id_{mode}", recordid)

    def getrecords_level(self, stat, mode):
        return [self.getrecord(level, stat, mode) for level in GameLevels]

    def getrecordIDs_level(self, stat, mode):
        return [self.getrecordID(level, stat, mode) for level in GameLevels]

    def update_3_level_cache_record(self, realname: str, index: str, mode: str):
        key = f"player_{index}_{mode}_{self.id}"
        cache.hset(key, "name", realname)
        for level in GameLevels:
            cache.hset(key, level, self.getrecord(level, index, mode))
            recordid = self.getrecordID(level, index, mode)
            cache.hset(key, f"{level}_id", "None" if recordid is None else recordid)
        s = float(
            self.getrecord("b", index, mode)
            + self.getrecord("i", index, mode)
            + self.getrecord("e", index, mode),
        )
        cache.hset(key, "sum", s)
        cache.zadd(f"player_{index}_{mode}_ids", {self.id: s})

    # 删除mysql中该用户所有的记录。删录像时用
    def del_user_record_sql(self):
        for mode in GameModes:
            for stat in RankingGameStats:
                for level in GameLevels:
                    self.setrecord(
                        level, stat, mode,
                        DefaultRankingScores[stat],
                    )
                    self.setrecordID(level, stat, mode, None)
        self.save(update_fields=record_update_fields)

    # 删除redis中该用户所有的记录。删录像、删用户时用
    def del_user_record_redis(self):
        for mode in GameModes:
            for stat in RankingGameStats:
                cache.delete(f"player_{stat}_{mode}_{self.id}")
                cache.zrem(f"player_{stat}_{mode}_ids", self.id)
