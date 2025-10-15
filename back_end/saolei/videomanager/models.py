# -*- coding: utf-8 -*-
import json
import logging

from django.db import models
from django_redis import get_redis_connection

from config.global_settings import DefaultRankingScores, MaxSizes, RankingGameStats, record_update_fields
from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from utils import ComplexEncoder
from utils.cmp import isbetter
from .fields import RestrictedFileField

cache = get_redis_connection("saolei_website")
logger = logging.getLogger('videomanager')


class ExpandVideoModel(models.Model):
    # video = models.OneToOneField(VideoModel, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=MaxSizes.IDENTIFIER, default="")
    stnb = models.FloatField(default=0.0)


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

def divideByTimeExpression(expr: models.Expression):
    return models.Case(models.When(timems=0, then=models.Value(0.0)), default=expr / models.F('timems') * models.Value(1000), output_field=models.FloatField())


# 基本的录像模型，最小限度展示录像信息
class VideoModel(models.Model):
    # 用户
    player = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # 服务器端文件相对路径
    file = RestrictedFileField(
        upload_to="videos/%Y%m%d/", max_length=100, max_upload_size=MaxSizes.VIDEOFILE)
    file_size = models.PositiveIntegerField(default=0)
    url_web = models.TextField(max_length=255, blank=True, default="")
    url_file = models.TextField(max_length=255, blank=True, default="")
    video = models.OneToOneField(
        ExpandVideoModel, on_delete=models.CASCADE, related_name="+")
    # file = models.FileField(upload_to="/assets/videos")
    # 上传时间，兼最近状态变化时间、更新时间（冻结后会刷新）
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    # 录像自带时间戳，可被用户篡改，用于用户自用。实际上无时区，因为Django限制，固定时区为UTC。
    end_time = models.DateTimeField(null=True, blank=True)
    # 审核状态
    state = models.CharField(
        max_length=1, choices=MS_TextChoices.State.choices, default=MS_TextChoices.State.PLAIN)
    ongoing_tournament = models.BooleanField(default=False)
    # 软件: "a"->avf; "e"->evf; "u" ->url(未下载);
    software = models.CharField(max_length=MaxSizes.SOFTWARE, choices=MS_TextChoices.Software.choices)
    # 难度
    level = models.CharField(
        max_length=MaxSizes.GAMELEVEL, choices=MS_TextChoices.Level.choices)
    # 游戏模式，evf标准
    # https://github.com/eee555/ms_toollib/tree/main/base#readme
    mode = models.CharField(
        max_length=MaxSizes.GAMEMODE, choices=MS_TextChoices.Mode.choices, default=MS_TextChoices.Mode.STD)
    # 0.000-999.999
    timems = models.PositiveIntegerField(
        default=DefaultRankingScores["timems"])  # 整数形式存储的毫秒数。
    # 0-32767
    bv = models.PositiveSmallIntegerField(null=True)
    bvs = models.GeneratedField(expression=models.Case(models.When(timems=0, then=models.Value(0.0)), default=models.F(
        'bv') / models.F('timems') * models.Value(1000), output_field=models.FloatField()), output_field=models.FloatField(), db_persist=True)

    left = models.PositiveSmallIntegerField(null=True)
    right = models.PositiveSmallIntegerField(null=True)
    double = models.PositiveSmallIntegerField(null=True)
    cl = models.GeneratedField(expression=models.F('left') + models.F('right') + models.F(
        'double'), output_field=models.PositiveSmallIntegerField(), db_persist=True)

    left_ce = models.PositiveSmallIntegerField(null=True)
    right_ce = models.PositiveSmallIntegerField(null=True)
    double_ce = models.PositiveSmallIntegerField(null=True)
    ce = models.GeneratedField(expression=models.F('left_ce') + models.F('right_ce') + models.F(
        'double_ce'), output_field=models.PositiveSmallIntegerField(), db_persist=True)

    # 需要处理除零错误
    left_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('left')), output_field=models.FloatField(), db_persist=True)
    right_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('right')), output_field=models.FloatField(), db_persist=True)
    double_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('double')), output_field=models.FloatField(), db_persist=True)
    cl_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('cl')), output_field=models.FloatField(), db_persist=True)

    left_ces = models.GeneratedField(expression=divideByTimeExpression(
        models.F('left_ce')), output_field=models.FloatField(), db_persist=True)
    right_ces = models.GeneratedField(expression=divideByTimeExpression(
        models.F('right_ce')), output_field=models.FloatField(), db_persist=True)
    double_ces = models.GeneratedField(expression=divideByTimeExpression(
        models.F('double_ce')), output_field=models.FloatField(), db_persist=True)
    ce_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('ce')), output_field=models.FloatField(), db_persist=True)

    path = models.FloatField(null=True)
    flag = models.PositiveSmallIntegerField(null=True)
    op = models.PositiveSmallIntegerField(null=True)
    isl = models.PositiveSmallIntegerField(null=True)

    flag_s = models.GeneratedField(expression=divideByTimeExpression(
        models.F('flag')), output_field=models.FloatField(), db_persist=True)
    ioe = models.GeneratedField(expression=models.F(
        'bv') / models.F('cl'), output_field=models.FloatField(), db_persist=True)
    thrp = models.GeneratedField(expression=models.F(
        'bv') / models.F('ce'), output_field=models.FloatField(), db_persist=True)
    corr = models.GeneratedField(expression=models.F(
        'ce') / models.F('cl'), output_field=models.FloatField(), db_persist=True)

    cell0 = models.PositiveSmallIntegerField(null=True)
    cell1 = models.PositiveSmallIntegerField(null=True)
    cell2 = models.PositiveSmallIntegerField(null=True)
    cell3 = models.PositiveSmallIntegerField(null=True)
    cell4 = models.PositiveSmallIntegerField(null=True)
    cell5 = models.PositiveSmallIntegerField(null=True)
    cell6 = models.PositiveSmallIntegerField(null=True)
    cell7 = models.PositiveSmallIntegerField(null=True)
    cell8 = models.PositiveSmallIntegerField(null=True)

    # 暂时的解决方案
    @property
    def stnb(self):
        return self.video.stnb

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
        if self.ongoing_tournament and name == 'newest_queue':
            return
        cache.hset(name, self.id, json.dumps({
            "state": self.state,
            "tournament": self.ongoing_tournament,
            "software": self.software,
            "time": self.upload_time,
            "player": self.player.realname,
            "player_id": self.player.id,
            "level": self.level,
            "mode": self.mode,
            "timems": self.timems,
            "bv": self.bv,
            "cl": self.cl,
            "ce": self.ce,
        }, cls=ComplexEncoder))

    def pop_redis(self, name: str):
        cache.hdel(name, self.id)

    def update_video_num(self, add=True):
        userms = self.player.userms
        # add = True：新增录像；add = False：删除录像
        if self.mode == MS_TextChoices.Mode.STD:
            userms.video_num_std += 1 if add else -1
        elif self.mode == MS_TextChoices.Mode.NF:
            userms.video_num_nf += 1 if add else -1
        elif self.mode == MS_TextChoices.Mode.JSW:
            userms.video_num_ng += 1 if add else -1
        elif self.mode == MS_TextChoices.Mode.BZD:
            userms.video_num_dg += 1 if add else -1

        if self.level == MS_TextChoices.Level.BEGINNER:
            userms.video_num_beg += 1 if add else -1
        elif self.level == MS_TextChoices.Level.INTERMEDIATE:
            userms.video_num_int += 1 if add else -1
        elif self.level == MS_TextChoices.Level.EXPERT:
            userms.video_num_exp += 1 if add else -1

        if add:
            # 给高玩自动扩容
            if self.mode == MS_TextChoices.Mode.STD and self.level == MS_TextChoices.Level.EXPERT:
                if self.timems < 100000 and userms.video_num_limit < 200:
                    userms.video_num_limit = 1000
                if self.timems < 60000 and userms.video_num_limit < 500:
                    userms.video_num_limit = 3000
                if self.timems < 50000 and userms.video_num_limit < 600:
                    userms.video_num_limit = 5000
                if self.timems < 40000 and userms.video_num_limit < 800:
                    userms.video_num_limit = 8000
                if self.timems < 30000 and userms.video_num_limit < 1000:
                    userms.video_num_limit = 10000

        userms.save(update_fields=["video_num_limit", "video_num_total", "video_num_beg", "video_num_int",
                    "video_num_exp", "video_num_std", "video_num_nf", "video_num_ng", "video_num_dg"])

    # 检查某录像是否打破个人纪录
    def checkPB(self, mode):
        user: UserProfile = self.player
        userms: UserMS = user.userms
        for statname in RankingGameStats:
            stat = getattr(self, statname)
            if stat is not None and isbetter(statname, stat, userms.getrecord(self.level, statname, mode)):
                self.update_news_queue(statname, mode)
                userms.setrecord(self.level, statname, mode, stat)
                userms.setrecordID(self.level, statname, mode, self.video.id)
                user.check_ms_ranking(statname, mode)

    # 增量式地更新用户的记录
    def update_personal_record(self):
        if self.state != MS_TextChoices.State.OFFICIAL or self.ongoing_tournament:
            return
        user: UserProfile = self.player
        ms_user: UserMS = user.userms

        if self.mode == MS_TextChoices.Mode.NF or self.mode == MS_TextChoices.Mode.STD:
            self.checkPB("std")

        if self.mode == MS_TextChoices.Mode.NF:
            self.checkPB("nf")

        if self.mode == MS_TextChoices.Mode.JSW:
            self.checkPB("ng")

        if self.mode == MS_TextChoices.Mode.BZD:
            self.checkPB("dg")

        # 改完记录，存回数据库
        ms_user.save(update_fields=record_update_fields)

    # 确定用户破某个纪录后，更新redis破纪录的记录，显示在首页用
    def update_news_queue(self, index: str, mode: str):
        user: UserProfile = self.player
        ms_user: UserMS = user.userms
        if ms_user.e_timems_std >= 60000 and (index != "timems" or self.level != "e"):
            return
        # print(f"{type(index)} {index}") # 调试用
        value = f"{getattr(self, index) / 1000:.3f}" if index == "timems" else f"{getattr(self, index):.3f}"
        delta_number = getattr(self, index) - \
            ms_user.getrecord(self.level, index, mode)
        if index == "timems":
            delta_number /= 1000
        # 看有没有存纪录录像的id，间接判断有没有纪录
        if ms_user.getrecordID(self.level, index, mode):
            delta = f"{delta_number:.3f}"
        else:
            delta = "新"
        cache.lpush("news_queue", json.dumps({
            "time": self.upload_time,
            "player": user.realname,
            "player_id": self.player.id,
            "video_id": self.id,
            "index": index,
            "mode": mode,
            "level": self.level,
            "value": value,
            "delta": delta}, cls=ComplexEncoder))

    def update_redis(self):
        user: UserProfile = self.player
        if self.state == MS_TextChoices.State.PLAIN:
            logger.info(f'用户 {user.username}#{user.id} 录像#{self.id} 机审失败')
            self.update_video_num()
        elif self.state == MS_TextChoices.State.IDENTIFIER:
            logger.info(f'用户 {user.username}#{user.id} 录像#{self.id} 标识不匹配')
            if not self.ongoing_tournament:
                self.push_redis("newest_queue")
            self.update_video_num()
        elif self.state == MS_TextChoices.State.FROZEN:
            logger.info(f'用户 {user.username}#{user.id} 录像#{self.id} 不合法')
            self.push_redis("freeze_queue")
        elif self.state == MS_TextChoices.State.OFFICIAL:  # 合法
            logger.info(f'用户 {user.username}#{user.id} 录像#{self.id} 机审成功')
            if not self.ongoing_tournament:
                self.push_redis("newest_queue")
                self.update_personal_record()
            self.update_video_num()
