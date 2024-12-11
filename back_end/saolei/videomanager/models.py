# -*- coding: utf-8 -*-
from django.db import models
from .fields import RestrictedFileField
from userprofile.models import UserProfile
from config.global_settings import *
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
import json
from utils import ComplexEncoder
from config.text_choices import MS_TextChoices

class ExpandVideoModel(models.Model):
    # video = models.OneToOneField(VideoModel, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=80)
    # 0-32767
    left = models.PositiveSmallIntegerField()
    right = models.PositiveSmallIntegerField()
    double = models.PositiveSmallIntegerField()
    cl = models.PositiveSmallIntegerField()
    left_s = models.FloatField()
    right_s = models.FloatField()
    double_s = models.FloatField()
    cl_s = models.FloatField()
    path = models.FloatField()
    flag = models.PositiveSmallIntegerField()
    flag_s = models.FloatField()
    stnb = models.FloatField()
    rqp = models.FloatField()
    ioe = models.FloatField()
    thrp = models.FloatField()
    corr = models.FloatField()
    ce = models.PositiveSmallIntegerField()
    ce_s = models.FloatField()
    op = models.PositiveSmallIntegerField()
    isl = models.PositiveSmallIntegerField()
    cell0 = models.PositiveSmallIntegerField()
    cell1 = models.PositiveSmallIntegerField()
    cell2 = models.PositiveSmallIntegerField()
    cell3 = models.PositiveSmallIntegerField()
    cell4 = models.PositiveSmallIntegerField()
    cell5 = models.PositiveSmallIntegerField()
    cell6 = models.PositiveSmallIntegerField()
    cell7 = models.PositiveSmallIntegerField()
    cell8 = models.PositiveSmallIntegerField()
    

# 其他类：checksum_ok, mode

# @receiver(post_save, sender=VideoModel)
# def create_expand_video(sender, instance, created, **kwargs):
#    print(kwargs)
#    if created:
#        ExpandVideoModel.objects.create(user=instance)

# @receiver(post_save, sender=VideoModel)
# def save_expand_video(sender, instance, **kwargs):
#     instance.profile.save()


# class File(models.Model):
#     file = RestrictedFileField(upload_to=user_directory_path, max_length=100,
# content_types=['application/pdf', 'application/excel', 'application/msword',
# 'text/plain', 'text/csv', 'application/zip',
# max_upload_size=5242880,)


# class Image(models.Model):
#     file = RestrictedFileField(upload_to=user_directory_path, max_length=100,
# content_types=['image/jpeg', 'image/gif', 'image/gif', 'image/bmp', 'image/tiff'],
# max_upload_size=5242880,)




# 基本的录像模型，最小限度展示录像信息
class VideoModel(models.Model):
    # 用户
    player = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # 服务器端文件相对路径
    file = RestrictedFileField(
        upload_to="videos/%Y%m%d/", max_length=100, max_upload_size=MaxSizes.videofile,)
    video = models.OneToOneField(ExpandVideoModel, on_delete=models.CASCADE, related_name="+")
    # file = models.FileField(upload_to="/assets/videos")
    # 上传时间，兼最近状态变化时间、更新时间（冻结后会刷新）
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    # 审核状态
    state = models.CharField(
        max_length=1, choices=MS_TextChoices.State.choices, default=MS_TextChoices.State.PLAIN)
    # 软件: "a"->avf; "e"->evf
    software = models.CharField(max_length=MaxSizes.software)
    # 难度
    level = models.CharField(max_length=MaxSizes.gamelevel, choices=MS_TextChoices.Level.choices)
    # 游戏模式，evf标准
    # https://github.com/eee555/ms_toollib/tree/main/base#readme
    mode = models.CharField(
        max_length=MaxSizes.gamemode, choices=MS_TextChoices.Mode.choices, default=MS_TextChoices.Mode.STD)
    # 0.000-999.999
    timems = models.PositiveIntegerField(default=DefaultRankingScores["timems"]) # 整数形式存储的毫秒数。
    # 0-32767
    bv = models.PositiveSmallIntegerField()
    bvs = models.GeneratedField(expression = models.Case(models.When(timems=0,then=models.Value(0.0)), default=models.F('bv') / models.F('timems') * models.Value(1000), output_field = models.FloatField()), output_field = models.FloatField(), db_persist = True)

    # 暂时的解决方案
    def __getattr__(self, name):
        if name == "stnb":
            return self.video.stnb
        elif name == "ioe":
            return self.video.ioe
        elif name == "path":
            return self.video.path
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __str__(self):
        return f'level: {self.level}, timems: {self.timems}, 3BV: {self.bv}'
    
    class Meta:
        indexes = [
            models.Index(fields=['level'], name='level_idx'),
            models.Index(fields=['mode'], name='mode_idx'),
            models.Index(fields=['bv'], name='bv_idx'),
            models.Index(fields=['bvs'], name='bvs_idx'),
            models.Index(fields=['timems'], name='timems_idx'),
            models.Index(fields=['state'], name='state_idx'),
        ]

    def push_redis(self, name: str):
        cache.hset(name, self.id, json.dumps({
            "state": self.state,
            "software": self.software,
            "time": self.upload_time,
            "player": self.player.realname,
            "player_id": self.player.id,
            "level": self.level,
            "mode": self.mode,
            "timems": self.timems,
            "bv": self.bv,
            "bvs": self.bvs,
            "identifier": self.video.identifier}, cls=ComplexEncoder))
        
    def pop_redis(self, name: str):
        cache.hdel(name, self.id)

