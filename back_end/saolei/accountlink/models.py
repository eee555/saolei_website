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
    id = models.IntegerField(primary_key=True)
    update_time = models.DateTimeField(auto_now_add=True)
    # 和utils.update_saolei_account同步更新attribute表