# -*- coding: utf-8 -*-
from django.db import models
from userprofile.models import UserProfile

# 用于验证的队列
class AccountLinkQueue(models.Model):
    class Platform(models.TextChoices):
        MSGAMES = 'a', ('Authoritative Minesweeper')
        SAOLEI = 'c', ('扫雷网')
        WOM = 'w', ('Minesweeper.Online')

    platform = models.CharField(max_length=1, null=False, choices=Platform.choices)
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
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_saolei')
    update_time = models.DateTimeField()

    name = models.CharField(max_length=10) # 姓名，10应该够了吧
    total_views = models.PositiveIntegerField() # 综合人气

    beg_count = models.PositiveSmallIntegerField() # 初级录像数量
    int_count = models.PositiveSmallIntegerField() # 中级录像数量
    exp_count = models.PositiveSmallIntegerField() # 高级录像数量

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
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_msgames')
    update_time = models.DateTimeField()

    name = models.CharField(max_length=128)
    local_name = models.CharField(max_length=128)
    # country = models.CharField() # country和state应该是二合一的枚举类型
    # state = models.CharField()
    joined = models.DateField()
    # mouse_brand = models.CharField(max_length=128) # 枚举
    # mouse_type = models.CharField(max_length=128) # 枚举
    # mouse_model = models.CharField() # 用户自己随便填的，需要审查

class AccountWorldOfMinesweeper(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_wom')
    update_time = models.DateTimeField(auto_now_add=True)

    # name 有的用户名过不了审
    # country 有争议
    trophy = models.PositiveSmallIntegerField()

    experience = models.PositiveIntegerField()
    honour = models.PositiveIntegerField()

    minecoin = models.PositiveIntegerField()
    gem = models.PositiveIntegerField()
    coin = models.PositiveIntegerField()
    arena_ticket = models.PositiveIntegerField()
    equipment = models.PositiveIntegerField()
    part = models.PositiveIntegerField()
    
    arena_point = models.PositiveSmallIntegerField() # 最高80
    max_difficulty = models.PositiveIntegerField()
    win = models.PositiveIntegerField()
    last_season = models.PositiveSmallIntegerField()

    b_t_ms = models.PositiveIntegerField(null=True)
    i_t_ms = models.PositiveIntegerField(null=True)
    e_t_ms = models.PositiveIntegerField(null=True)
    s_t_ms = models.PositiveIntegerField(null=True)

    b_ioe = models.FloatField()
    i_ioe = models.FloatField()
    e_ioe = models.FloatField()
    s_ioe = models.FloatField()

    b_mastery = models.PositiveSmallIntegerField()
    i_mastery = models.PositiveSmallIntegerField()
    e_mastery = models.PositiveSmallIntegerField()

    b_winstreak = models.PositiveSmallIntegerField()
    i_winstreak = models.PositiveSmallIntegerField()
    e_winstreak = models.PositiveSmallIntegerField()

    # 主页只显示一个
    # b_endurance = models.TimeField()
    # i_endurance = models.TimeField()
    # e_endurance = models.TimeField()