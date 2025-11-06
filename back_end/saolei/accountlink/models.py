# -*- coding: utf-8 -*-
import re
import requests

from django.db import models
from django.core.files.base import ContentFile

from userprofile.models import UserProfile
from videomanager.models import VideoModel
from utils.exceptions import ExceptionToResponse
from utils.parser import MSVideoParser
from msuser.models import UserMS
from config.text_choices import MS_TextChoices
from identifier.models import Identifier
from tournament.utils import video_checkin
from utils.saolei import SaoleiUtils, SaoleiUserInfo


class Platform(models.TextChoices):
    MSGAMES = 'a', ('Authoritative Minesweeper')
    QQ = 'q', ('腾讯QQ')
    SAOLEI = 'c', ('扫雷网')
    WOM = 'w', ('Minesweeper.Online')

class SaoleiVideoState(models.TextChoices):
    NOTEXIST = 'n', ('不存在')
    PENDING = 'p', ('未审核')
    FROZEN = 'f', ('已冻结')
    OFFICIAL = 'o', ('正常')

class SaoleiVideoImportState(models.TextChoices):
    NOTPLANNED = 'n', ('未计划')
    QUEUEING = 'q', ('排队中')
    IMPORTING = 'i', ('导入中')
    IMPORTED = 'd', ('已导入')
    FAILED = 'f', ('导入失败')


# 用于验证的队列
class AccountLinkQueue(models.Model):
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
    update_time = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=10, default="")  # 姓名，10应该够了吧
    total_views = models.PositiveIntegerField(null=True)  # 综合人气

    beg_count = models.PositiveSmallIntegerField(null=True)  # 初级录像数量
    int_count = models.PositiveSmallIntegerField(null=True)  # 中级录像数量
    exp_count = models.PositiveSmallIntegerField(null=True)  # 高级录像数量

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

    def import_video_list(self, page: int):
        saolei_user = SaoleiUserInfo(saolei_id=self.id)
        video_list = SaoleiUtils.get_video_list(saolei_user.videos_url(page=page))
        existing_video_ids = list(VideoSaolei.objects.filter(id__in=[info.video_id for info in video_list]).values_list('id', flat=True))

        count = 0
        new_video_list = []
        for video_info in video_list:
            if video_info.video_id not in existing_video_ids:
                VideoSaolei.objects.create(id=video_info.video_id, user=self, upload_time=video_info.upload_time, level=video_info.level, bv=video_info.bv, timems=video_info.timems, nf=video_info.nf)
                count += 1
                new_video_list.append(video_info)

        return new_video_list


class VideoSaolei(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    user = models.ForeignKey(AccountSaolei, on_delete=models.DO_NOTHING, related_name='videos')
    upload_time = models.DateTimeField()
    level = models.CharField(max_length=1, choices=MS_TextChoices.Level.choices)
    bv = models.PositiveSmallIntegerField(default=0)
    timems = models.PositiveIntegerField(default=0)
    nf = models.BooleanField(default=False)
    state = models.CharField(max_length=1, choices=SaoleiVideoState.choices)
    import_state = models.CharField(max_length=1, choices=SaoleiVideoImportState.choices, default=SaoleiVideoImportState.NOTPLANNED)
    import_video = models.OneToOneField(VideoModel, on_delete=models.SET_NULL, null=True)

    @property
    def url(self):
        return f'http://saolei.wang/Video/Show.asp?Id={self.id}'
    
    def get_download_url(self):
        response = requests.get(url=self.url, timeout=5)
        response.encoding = 'GB2312'
        if response.text == '''<script language="JavaScript">alert('此录象不存在!');</script><script language=JavaScript>top.location=top.location</script>''':
            self.verified = False
            return None
        if '此录像尚未通过审核！' in response.text or '为什么冻结？' in response.text:
            self.verified = False
        return 'http://saolei.wang/' + re.search(r"PlayVideo\('([^']+)'\)", response.text).group(1)

    def run_import(self):
        if self.import_state == SaoleiVideoImportState.IMPORTING:
            return
        self.import_state = SaoleiVideoImportState.IMPORTING
        self.save()
        try:
            download_url = self.get_download_url()
            file_name = download_url.split('/')[-1]
            response = requests.get(url=self.get_download_url(), timeout=5)
            file_size = response.headers.get('Content-Length')
            if file_size is None:
                raise ExceptionToResponse(obj='import', category='response')
            
            collisions = VideoModel.objects.filter(file_size=file_size)
            for collision in collisions:
                if collision.file.read() == response.content:
                    collision.url_file = download_url
                    collision.url_web = self.url
                    if collision.upload_time > self.upload_time:
                        collision.upload_time = self.upload_time
                    collision.ongoing_tournament = False
                    collision.save()
                    self.import_state = SaoleiVideoImportState.IMPORTED
                    self.import_video = collision
                    self.save()
                    return
            
            parser = MSVideoParser(ContentFile(response.content, file_name))
            user = self.user.parent

            if not user.userms:
                user.userms = UserMS.objects.create()
            if not Identifier.verify(parser.identifier, user.userms) and parser.state == MS_TextChoices.State.OFFICIAL:
                parser.state = MS_TextChoices.State.IDENTIFIER

            video = VideoModel.create_from_parser(parser, user)
            video_checkin(video, parser.tournament_identifiers)
            video.update_redis()
            self.import_video = video
            self.import_state = SaoleiVideoImportState.IMPORTED
            self.save()
        except requests.exceptions.ConnectionError as e:
            self.import_state = SaoleiVideoImportState.FAILED
            self.save()
            raise ExceptionToResponse(obj='import', category='connection')
        except requests.exceptions.ReadTimeout as e:
            self.import_state = SaoleiVideoImportState.FAILED
            self.save()
            raise ExceptionToResponse(obj='import', category='readtimeout')
        except Exception as e:
            self.import_state = SaoleiVideoImportState.FAILED
            self.save()
            raise e


class AccountMinesweeperGames(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_msgames')
    update_time = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=128, default="")
    local_name = models.CharField(max_length=128, default="")
    # country = models.CharField() # country和state应该是二合一的枚举类型
    # state = models.CharField()
    joined = models.DateField(null=True)
    # mouse_brand = models.CharField(max_length=128) # 枚举
    # mouse_type = models.CharField(max_length=128) # 枚举
    # mouse_model = models.CharField() # 用户自己随便填的，需要审查


class AccountWorldOfMinesweeper(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_wom')
    update_time = models.DateTimeField(auto_now=True)

    # name 有的用户名过不了审
    # country 有争议
    trophy = models.PositiveSmallIntegerField(null=True)

    experience = models.PositiveIntegerField(null=True)
    honour = models.PositiveIntegerField(null=True)

    minecoin = models.PositiveIntegerField(null=True)
    gem = models.PositiveIntegerField(null=True)
    coin = models.PositiveIntegerField(null=True)
    arena_ticket = models.PositiveIntegerField(null=True)
    equipment = models.PositiveIntegerField(null=True)
    part = models.PositiveIntegerField(null=True)

    arena_point = models.PositiveSmallIntegerField(null=True)  # 最高80
    max_difficulty = models.PositiveIntegerField(null=True)
    win = models.PositiveIntegerField(null=True)
    last_season = models.PositiveSmallIntegerField(null=True)

    b_t_ms = models.PositiveIntegerField(null=True)
    i_t_ms = models.PositiveIntegerField(null=True)
    e_t_ms = models.PositiveIntegerField(null=True)

    b_ioe = models.FloatField(null=True)
    i_ioe = models.FloatField(null=True)
    e_ioe = models.FloatField(null=True)

    b_mastery = models.PositiveSmallIntegerField(null=True)
    i_mastery = models.PositiveSmallIntegerField(null=True)
    e_mastery = models.PositiveSmallIntegerField(null=True)

    b_winstreak = models.PositiveSmallIntegerField(null=True)
    i_winstreak = models.PositiveSmallIntegerField(null=True)
    e_winstreak = models.PositiveSmallIntegerField(null=True)

    # 主页只显示一个
    # b_endurance = models.TimeField()
    # i_endurance = models.TimeField()
    # e_endurance = models.TimeField()


# 使用QQ互联提供的登录接口需要开发者注册，步骤繁琐，不利于去中心化
class AccountQQ(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    parent = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='account_qq')


PLATFORM_CONFIG = {
    Platform.MSGAMES: {
        'model': AccountMinesweeperGames,
        'related_name': 'account_msgames',
    },
    Platform.SAOLEI: {
        'model': AccountSaolei,
        'related_name': 'account_saolei',
    },
    Platform.WOM: {
        'model': AccountWorldOfMinesweeper,
        'related_name': 'account_wom',
    },
    Platform.QQ: {
        'model': AccountQQ,
        'related_name': 'account_qq',
    },
}
