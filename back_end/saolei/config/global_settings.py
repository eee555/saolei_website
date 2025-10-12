# 全局设置，约定不可变
# 全局可变量写在settings.py的GLOBAL_VARIABLES


# 数据大小限制
class MinSizes:
    PASSWORD = 6


class MaxSizes:
    AVATAR = 1024 * 300  # 头像图片，大小限制在300k以内。
    COUNTRY = 2  # Alpha-2 code from ISO3166
    EMAIL = 255
    EMAILCODE = 6  # 邮箱验证码
    FIRSTNAME = 255
    GAMELEVEL = 1  # 级别（初中高）
    GAMEMODE = 2  # 模式（无猜）
    IDENTIFIER = 80  # 标识
    LASTNAME = 255
    PASSWORD = 20  # 密码
    SIGNATURE = 4095  # 个性签名的长度，考虑了一些比较啰嗦的语言。
    SOFTWARE = 1
    USERNAME = 30  # 用户名，行业习惯的上限
    VIDEOFILE = 5 * 1024 * 1024  # 录像文件


# 默认修改个人资料的次数
class DefaultChances:
    NAME = 1  # 名字
    AVATAR = 2  # 头像
    SIGNATURE = 2  # 签名


# 级别
GameLevels = ["b", "i", "e"]
GameModes = ["std", "nf", "ng", "dg"]
RankingGameStats = ["timems", "bvs", "stnb", "ioe", "path"]
DefaultRankingScores = {"timems": 999999, "bvs": 0.0, "stnb": 0.0, "ioe": 0.0, "path": 100000.0}
VideoModeToName = {"00": "std", "12": "std"}

record_update_fields = []
for mode in GameModes:
    for stat in RankingGameStats:
        for level in GameLevels:
            record_update_fields.append(f"{level}_{stat}_{mode}")
            record_update_fields.append(f"{level}_{stat}_id_{mode}")
