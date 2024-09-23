# -*- coding: utf-8 -*-
from django.db import models
from userprofile.models import UserProfile

# 用于验证的队列
class AccountLinkQueue(models.Model):
    platform = models.CharField(max_length=1, null=False)
    identifier = models.CharField(max_length=128, null=False)
    userprofile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

# 网站编码 website code
# a - Authoritative Minesweeper
# c - China ranking (saolei.wang)
# g - Minesweeper GO
# l - League of Minesweeper
# s - Scoreganizer
# w - World of Minesweeper
# B - Bilibili
# D - Discord
# F - Facebook
# G - GitHub
# R - Reddit
# S - Speedrun.com
# T - Tieba
# W - Weibo
# X - X
# Y - YouTube
# Z - Zhihu

# 扫雷网账号信息
class AccountSaolei(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    update_time = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=10) # 姓名，10应该够了吧
    total_views = models.PositiveIntegerField(default=0) # 综合人气

    beg_count = models.PositiveSmallIntegerField(default=0) # 初级录像数量
    int_count = models.PositiveSmallIntegerField(default=0) # 中级录像数量
    exp_count = models.PositiveSmallIntegerField(default=0) # 高级录像数量

    # time纪录，单位毫秒
    b_t_ms = models.PositiveIntegerField(null=True)
    i_t_ms = models.PositiveIntegerField(null=True)
    e_t_ms = models.PositiveIntegerField(null=True)
    s_t_ms = models.PositiveIntegerField(null=True)

    # bvs纪录，单位0.01。大概不会有人bvs超过300吧？大概吧？
    b_b_cent = models.PositiveSmallIntegerField(null=True)
    i_b_cent = models.PositiveSmallIntegerField(null=True)
    e_b_cent = models.PositiveSmallIntegerField(null=True)
    s_b_cent = models.PositiveSmallIntegerField(null=True)

class AccountMinesweeperGames(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    update_time = models.DateTimeField(auto_now_add=True)

class AccountWorldOfMinesweeper(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    update_time = models.DateTimeField(auto_now_add=True)

    # name = models.CharField()
    # local_name = models.CharField()
    # country = models.CharField()
    # state = models.CharField()
    # joined = models.DateField()
    # mouse_brand = models.CharField()
    # mouse_type = models.CharField()
    # mouse_model = models.CharField() 用户自己随便填的，需要审查