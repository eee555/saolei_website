import string
import secrets
from django.db import models
from userprofile.models import UserProfile
from videomanager.models import VideoModel
from config.text_choices import Tournament_TextChoices, MS_TextChoices
from config.tournaments import GSC_Defaults
from datetime import datetime, timezone
from model_utils.managers import InheritanceManager
from config.global_settings import MaxSizes
from identifier.models import Identifier


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

    def start(self):
        self.state = Tournament_TextChoices.State.ONGOING
        self.save()

    def end(self):
        self.state = Tournament_TextChoices.State.FINISHED
        self.save()
        self.videos.all().update(ongoing_tournament=False)
        for video in self.videos.all():
            video.update_redis()

    def refresh_state(self):
        if self.state == Tournament_TextChoices.State.PREPARING:
            if datetime.now(timezone.utc) > self.end_time:
                self.start()
                self.end()
            elif datetime.now(timezone.utc) >= self.start_time:
                self.start()
        elif self.state == Tournament_TextChoices.State.ONGOING:
            if datetime.now(timezone.utc) >= self.end_time:
                self.end()
            elif datetime.now(timezone.utc) < self.start_time:
                self.state = Tournament_TextChoices.State.PREPARING
                self.save()
        elif self.state == Tournament_TextChoices.State.FINISHED:
            if datetime.now(timezone.utc) < self.start_time:
                self.state = Tournament_TextChoices.State.PREPARING
                self.save()
            elif datetime.now(timezone.utc) < self.end_time:
                self.state = Tournament_TextChoices.State.ONGOING
                self.save()
        return

    def validate(self):
        if not self.start_time or not self.end_time or self.start_time >= self.end_time:
            return
        if self.state == Tournament_TextChoices.State.PENDING or self.state == Tournament_TextChoices.State.CANCELLED:
            self.state = Tournament_TextChoices.State.PREPARING
            self.save()
            self.refresh_state()

    def invalidate(self):
        if self.state != Tournament_TextChoices.State.AWARDED:
            self.state = Tournament_TextChoices.State.CANCELLED
            self.save()

    def add_participant(self, user: UserProfile):
        raise NotImplementedError("Subclasses of Tournament must implement the 'add_participant' method.")

    def add_video(self, video: VideoModel):
        self.videos.add(video)
        self.add_participant(video.player)


class GSCTournament(Tournament):
    order = models.PositiveSmallIntegerField(primary_key=True)  # 届数
    token = models.CharField(max_length=6, default='')  # 比赛标识

    @property
    def series(self):
        return Tournament_TextChoices.Series.GSC

    @property
    def name(self):
        return f'第{self.order}届金羊杯'

    @property
    def description(self):
        return ''

    def new_token(self):
        token = generate_GSC_token()
        while GSCTournament.objects.filter(token=token).exists() or TournamentParticipant.objects.filter(token=token).exists():
            token = generate_GSC_token()
        self.token = token
        self.save()

    def start(self):
        if self.token == '':
            self.new_token()
        super().start()

    def end(self):
        self.refresh_score()
        super().end()

    def add_participant(self, user: UserProfile):
        if not GSCParticipant.objects.filter(user=user, tournament=self).exists():
            GSCParticipant.objects.create(user=user, tournament=self, token=self.token, start_time=datetime.now(tz=timezone.utc))

    def refresh_score(self):
        for participant in GSCParticipant.objects.filter(tournament=self):
            participant.refresh()
        rank = 1
        for participant in GSCParticipant.objects.filter(tournament=self).order_by('t37'):
            participant.rank = rank
            participant.save()
            rank += 1


class GeneralTournament(Tournament):
    name = models.JSONField()
    description = models.JSONField()
    csv_head = models.JSONField()

    @property
    def series(self):
        return ''


class TournamentParticipant(models.Model):
    token = models.CharField(max_length=MaxSizes.IDENTIFIER)  # 比赛标识
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

    def refresh(self):
        videos = self.tournament.videos.filter(player=self.user)

        videos_b = videos.filter(level=MS_TextChoices.Level.BEGINNER, bv__gte=GSC_Defaults.B_BV_MIN)
        videos_bt = videos_b.order_by('timems')[:20].values_list('timems', flat=True)
        self.bt1st = videos_bt[0] if len(videos_bt) >= 1 else 10000
        self.bt20th = videos_bt[19] if len(videos_bt) >= 20 else 10000
        self.bt20sum = sum(videos_bt) + (20 - len(videos_bt)) * 10000

        videos_i = videos.filter(level=MS_TextChoices.Level.INTERMEDIATE, bv__gte=GSC_Defaults.I_BV_MIN)
        videos_it = videos_i.order_by('timems')[:12].values_list('timems', flat=True)
        self.it1st = videos_it[0] if len(videos_it) >= 1 else 60000
        self.it12th = videos_it[11] if len(videos_it) >= 12 else 60000
        self.it12sum = sum(videos_it) + (12 - len(videos_it)) * 60000

        videos_e = videos.filter(level=MS_TextChoices.Level.EXPERT, bv__gte=GSC_Defaults.E_BV_MIN)
        videos_et = videos_e.order_by('timems')[:5].values_list('timems', flat=True)
        self.et1st = videos_et[0] if len(videos_et) >= 1 else 240000
        self.et5th = videos_et[4] if len(videos_et) >= 5 else 240000
        self.et5sum = sum(videos_et) + (5 - len(videos_et)) * 240000

        self.save()
