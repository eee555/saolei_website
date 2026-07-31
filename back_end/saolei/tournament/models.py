from datetime import datetime, timezone
import secrets
import string

from django.db import models
from model_utils.managers import InheritanceManager

from config.global_settings import MaxSizes
from config.text_choices import Tournament_TextChoices
from config.tournaments import GSC_Defaults
from identifier.models import Identifier
from userprofile.models import UserProfile
from videomanager.models import VideoModel


def generate_random_token(length=4):
    """生成指定位数的随机字母数字混合码"""
    alphabet = string.ascii_letters + string.digits  # 大小写字母+数字
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_GSC_token(length=GSC_Defaults.TOKEN_LENGTH):
    return 'G' + ''.join(secrets.choice(string.digits) for _ in range(length))


class Tournament(models.Model):
    objects = InheritanceManager()
    start_time = models.DateTimeField(null=True)  # 比赛开始时间
    end_time = models.DateTimeField(null=True)  # 比赛结束时间
    state = models.CharField(max_length=1, choices=Tournament_TextChoices.State.choices, default=Tournament_TextChoices.State.PENDING)  # 比赛状态
    host = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='owned_tournaments')  # 主办方
    weight = models.PositiveIntegerField(default=0)  # 比赛总积分
    videos = models.ManyToManyField(VideoModel, related_name='tournaments')

    @property
    def series(self):
        raise NotImplementedError("Subclasses of Tournament must implement the 'series' property.")

    @property
    def name(self):
        raise NotImplementedError("Subclasses of Tournament must implement the 'name' property.")

    @property
    def description(self):
        raise NotImplementedError("Subclasses of Tournament must implement the 'description' property.")

    @property
    def participants(self):
        return TournamentParticipant.objects.filter(tournament=self)

    def validate(self):
        if not self.start_time or not self.end_time or self.start_time >= self.end_time:
            return
        if self.state == Tournament_TextChoices.State.PENDING or self.state == Tournament_TextChoices.State.CANCELLED:
            self.state = Tournament_TextChoices.State.NORMAL
            self.save(update_fields=['state'])

    def invalidate(self):
        if self.state != Tournament_TextChoices.State.AWARDED:
            self.state = Tournament_TextChoices.State.CANCELLED
            self.save(update_fields=['state'])

    def add_participant(self, user: UserProfile):
        raise NotImplementedError("Subclasses of Tournament must implement the 'add_participant' method.")

    def add_video(self, video: VideoModel):
        self.videos.add(video)
        self.add_participant(video.player)


class GSCTournament(Tournament):
    order = models.PositiveSmallIntegerField(primary_key=True)  # 届数
    token = models.CharField(max_length=6, default='', db_collation='utf8mb4_0900_as_cs')  # 比赛标识

    @property
    def series(self):
        return Tournament_TextChoices.Series.GSC

    @property
    def name(self):
        return {
            'zh': f'第{self.order}届金羊杯',
            'en': f'GSC#{self.order}',
        }

    @property
    def description(self):
        return ''

    def new_token(self):
        self.token = self.generate_unique_token()
        self.save(update_fields=['token'])

    @staticmethod
    def generate_unique_token():
        token = generate_GSC_token()
        while GSCTournament.objects.filter(token=token).exists() or TournamentParticipant.objects.filter(token=token).exists():
            token = generate_GSC_token()
        return token

    def validate(self):
        if not self.start_time or not self.end_time or self.start_time >= self.end_time:
            return
        if self.state == Tournament_TextChoices.State.PENDING or self.state == Tournament_TextChoices.State.CANCELLED:
            self.state = Tournament_TextChoices.State.NORMAL
            update_fields = ['state']
            if not self.token:
                self.token = self.generate_unique_token()
                update_fields.append('token')
            self.save(update_fields=update_fields)

    def add_participant(self, user: UserProfile):
        if not GSCParticipant.objects.filter(user=user, tournament=self).exists():
            GSCParticipant.objects.create(user=user, tournament=self, token=self.token, start_time=datetime.now(tz=timezone.utc))


class GeneralTournament(Tournament):
    name = models.JSONField()
    description = models.JSONField()
    csv_head = models.JSONField()

    @property
    def series(self):
        return ''


class TournamentParticipant(models.Model):
    token = models.CharField(max_length=MaxSizes.IDENTIFIER, db_collation='utf8mb4_0900_as_cs')  # 比赛标识
    arbiter_identifier = models.ForeignKey(Identifier, null=True, on_delete=models.PROTECT)  # 阿比特标识
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)  # 比赛
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)  # 用户
    start_time = models.DateTimeField(auto_now_add=True)  # 参赛时间
    end_time = models.DateTimeField(null=True, blank=True)  # 结束时间
    rank = models.PositiveIntegerField(null=True, blank=True)  # 排名
    rank_score = models.PositiveSmallIntegerField(default=0)  # 比赛积分

    class Meta:
        unique_together = ('tournament', 'user')

    def create(self, *args, **kwargs):
        """创建参赛者时生成唯一的token"""
        if not self.token:
            while True:
                token = generate_random_token()
                if not TournamentParticipant.objects.filter(token=token).exists():
                    self.token = token
                    break
        super().create(*args, **kwargs)

    @property
    def videos(self):
        return self.tournament.videos.filter(player=self.user)


class GeneralParticipant(TournamentParticipant):
    pass


class GSCParticipant(TournamentParticipant):
    bt1st = models.PositiveIntegerField(default=GSC_Defaults.BT)
    bt20th = models.PositiveIntegerField(default=GSC_Defaults.BT)
    bt20sum = models.PositiveIntegerField(default=GSC_Defaults.BT * 20)

    it1st = models.PositiveIntegerField(default=GSC_Defaults.IT)
    it12th = models.PositiveIntegerField(default=GSC_Defaults.IT)
    it12sum = models.PositiveIntegerField(default=GSC_Defaults.IT * 12)

    et1st = models.PositiveIntegerField(default=GSC_Defaults.ET)
    et5th = models.PositiveIntegerField(default=GSC_Defaults.ET)
    et5sum = models.PositiveIntegerField(default=GSC_Defaults.ET * 5)

    t37 = models.GeneratedField(
        expression=models.F('et5sum') + models.F('it12sum') + models.F('bt20sum'),
        output_field=models.PositiveIntegerField(),
        db_persist=True,
    )
