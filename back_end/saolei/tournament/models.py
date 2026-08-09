import secrets
import string

from django.db import models
from django.utils import timezone
from django_tasks_db.models import DBTaskResult
from model_utils.managers import InheritanceManager

from config.global_settings import MaxSizes
from config.text_choices import Tournament_TextChoices
from config.tournaments import GSC_Defaults
from identifier.models import Identifier
from tournament.utils import generate_random_token, insert_to_id_value_list_asc
from userprofile.models import UserProfile
from videomanager.models import VideoModel


def generate_GSC_token(length=GSC_Defaults.TOKEN_LENGTH):
    return 'G' + ''.join(secrets.choice(string.digits) for _ in range(length))


def default_weekly_classic_et():
    return [(0, 240000), (0, 240000)]


def default_weekly_classic_it():
    return [(0, 60000), (0, 60000), (0, 60000), (0, 60000), (0, 60000)]


class Tournament(models.Model):
    objects = InheritanceManager()
    subclass = models.CharField(max_length=1, choices=Tournament_TextChoices.Subclass.choices, default=Tournament_TextChoices.Subclass.GSC)  # 比赛子类
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

    def can_validate(self):
        return self.start_time is not None and self.end_time is not None and self.start_time < self.end_time

    def accept_checkin(self):
        now = timezone.now()
        return (
            self.state == Tournament_TextChoices.State.NORMAL
            and self.start_time is not None
            and self.end_time is not None
            and self.start_time <= now < self.end_time
        )

    def is_ended(self):
        return self.state == Tournament_TextChoices.State.AWARDED or (self.end_time is not None and self.end_time < timezone.now())

    def validate(self) -> list[str]:
        if not self.can_validate():
            return []
        if self.state == Tournament_TextChoices.State.PENDING or self.state == Tournament_TextChoices.State.CANCELLED:
            self.state = Tournament_TextChoices.State.NORMAL
            return ['state']
        return []

    def invalidate(self):
        if self.state != Tournament_TextChoices.State.AWARDED:
            self.state = Tournament_TextChoices.State.CANCELLED
            self.save(update_fields=['state'])

    def add_participant(self, user: UserProfile):
        raise NotImplementedError("Subclasses of Tournament must implement the 'add_participant' method.")

    @property
    def data(self):
        return {}

    def select_subclass(self):
        if type(self) is not Tournament:
            return self
        if self.subclass == Tournament_TextChoices.Subclass.WEEKLY:
            return WeeklyTournament.objects.filter(tournament_ptr_id=self.id).first() or self
        elif self.subclass == Tournament_TextChoices.Subclass.GSC:
            return GSCTournament.objects.filter(tournament_ptr_id=self.id).first() or self
        return self


class GSCTournament(Tournament):
    order = models.PositiveSmallIntegerField(primary_key=True)  # 届数
    _token = models.CharField(max_length=6, default='', db_column='token', db_collation='utf8mb4_0900_as_cs')  # 比赛标识
    task = models.ForeignKey(DBTaskResult, on_delete=models.SET_NULL, null=True)

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

    @property
    def data(self):
        return {
            'order': self.order,
            'token': self.token,
        }

    @property
    def token(self):
        if self.start_time is None or timezone.now() < self.start_time:
            return ''
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def new_token(self):
        self._token = self.generate_unique_token()

    @staticmethod
    def generate_unique_token():
        token = generate_GSC_token()
        while GSCTournament.objects.filter(_token=token).exists() or TournamentParticipant.objects.filter(token=token).exists():
            token = generate_GSC_token()
        return token

    def validate(self) -> list[str]:
        if not self.can_validate():
            return []
        if self.state == Tournament_TextChoices.State.PENDING or self.state == Tournament_TextChoices.State.CANCELLED:
            self.state = Tournament_TextChoices.State.NORMAL
            update_fields = ['state']
            if not self._token:
                self._token = self.generate_unique_token()
                update_fields.append('_token')
            return update_fields
        return []

    def add_participant(self, user: UserProfile):
        if not GSCParticipant.objects.filter(user=user, tournament=self).exists():
            GSCParticipant.objects.create(
                user=user,
                tournament=self,
                token=self._token,
                start_time=self.start_time,
                end_time=self.end_time,
            )


class WeeklyTournament(Tournament):
    year = models.PositiveSmallIntegerField()  # 年份
    week = models.PositiveSmallIntegerField()  # 期数
    task = models.ForeignKey(DBTaskResult, on_delete=models.SET_NULL, null=True)
    tournament_format = models.CharField(max_length=1, choices=Tournament_TextChoices.WeeklyFormat.choices, default=Tournament_TextChoices.WeeklyFormat.CLASSIC)

    @property
    def series(self):
        return Tournament_TextChoices.Series.WEEKLY

    @property
    def name(self):
        return {
            'zh': f'{self.year}年第{self.week}周打卡赛',
            'en': f'Weekly {self.year}#{self.week}',
        }

    @property
    def description(self):
        return ''

    @property
    def data(self):
        return {
            'year': self.year,
            'week': self.week,
            'tournament_format': self.tournament_format,
        }


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
    start_time = models.DateTimeField(default=timezone.now)  # 参赛时间
    end_time = models.DateTimeField(null=True, blank=True)  # 结束时间
    rank = models.PositiveIntegerField(null=True, blank=True)  # 排名
    rank_score = models.PositiveSmallIntegerField(default=0)  # 比赛积分

    class Meta:
        unique_together = ('tournament', 'user')

    def save(self, *args, **kwargs):
        """创建参赛者时生成唯一的token"""
        if self._state.adding and not self.token:
            while True:
                token = generate_random_token()
                if not TournamentParticipant.objects.filter(token=token).exists():
                    self.token = token
                    break
        super().save(*args, **kwargs)  # noqa: DJM100

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

    @property
    def user__id(self):
        return self.user_id

    @property
    def user__realname(self):
        return self.user.realname if self.user else None


class WeeklyParticipant(TournamentParticipant):
    classic_et = models.JSONField(default=default_weekly_classic_et)
    classic_it = models.JSONField(default=default_weekly_classic_it)
    classic_score = models.PositiveIntegerField(default=780000)

    class Meta:
        indexes = [
            models.Index(fields=['classic_score'], name='classic_score_idx'),
        ]

    def classic_add_e(self, video_id: int, timems: int):
        diff = self.classic_et[1][1] - timems
        if diff > 0:
            self.classic_score -= diff
            if timems < self.classic_et[0][1]:
                self.classic_et[1] = self.classic_et[0]
                self.classic_et[0] = (video_id, timems)
            else:
                self.classic_et[1] = (video_id, timems)
        return diff

    def classic_add_i(self, video_id: int, timems: int):
        diff = self.classic_it[4][1] - timems
        if diff > 0:
            self.classic_score -= diff
            insert_to_id_value_list_asc(self.classic_it, video_id, timems)
        return diff
