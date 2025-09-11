from django.db import models

from userprofile.models import UserProfile


# 收录的赛事
class Match(models.Model):
    # 赛事名称
    name = models.CharField(null=False, max_length=100)
    # 赛事的管理员，拥有上传、修改比赛结果的权限
    administrator = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE)
    # 赛事的总积分。将管理员上传的积分归一化后加给用户
    sum_score = models.PositiveBigIntegerField(null=False, default=0)
    # 赛事注册时间
    register_time = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    # 赛事注销时间
    unregister_time = models.DateTimeField(auto_now_add=True, verbose_name="注销时间")
    # 赛事的最小举办周期，预留，非强制
    cycle_min = models.PositiveIntegerField()
    # 赛事的平均举办周期，预留，非强制
    cycle_ave = models.PositiveIntegerField()
    # 赛事的最大举办周期，预留，非强制
    cycle_max = models.PositiveIntegerField()


# 扫雷用户的积分的增加记录
class UserMSScoreRank(models.Model):
    player = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE)
    # 增加积分的时间戳
    models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    # 增加的积分数值
    score = models.FloatField(null=False, default=100)
    # 比赛
    # score = models.FloatField(null=False, default=100)
