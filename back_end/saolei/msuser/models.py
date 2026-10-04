from django.db import models


def get_default_identifiers():
    return []


def VideoCountField():
    return models.IntegerField(null=False, default=0)


# 扫雷用户的标识、录像计数与上传额度
class UserMS(models.Model):
    # 用户的标识。管理员审核通过后可以自由使用该标识。
    identifiers = models.JSONField(default=get_default_identifiers)
    # 总录像数限制默认100，计划管理员可以修改。高水平玩家也可以增多。
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

    def __str__(self):
        return 'identifiers: {}'.format(self.identifiers)
