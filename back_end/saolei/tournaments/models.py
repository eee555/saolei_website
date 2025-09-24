import string
import secrets
from django.db import models
from userprofile.models import UserProfile
from videomanager.models import VideoModel
from config.text_choices import Tournament_TextChoices, MS_TextChoices
from config.tournaments import GSC_Defaults
from datetime import datetime

def generate_random_token(length=4):
    """生成指定位数的随机字母数字混合码"""
    alphabet = string.ascii_letters + string.digits  # 大小写字母+数字
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class Tournament(models.Model):
    start_time = models.DateTimeField() # 比赛开始时间
    end_time = models.DateTimeField() # 比赛结束时间
    state = models.CharField(max_length=1, choices=Tournament_TextChoices.State.choices, default=Tournament_TextChoices.State.PENDING) # 比赛状态
    host = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='owned_tournaments') # 主办方
    weight = models.PositiveIntegerField(default=0) # 比赛总积分
    videos = models.ManyToManyField(VideoModel, related_name='tournaments')


class GSCTournament(Tournament):
    order = models.PositiveSmallIntegerField(primary_key=True) # 届数
    token = models.CharField(max_length=6) # 比赛标识

    def start(self):
        self.token = 'G' + generate_random_token(5)
        self.state = Tournament_TextChoices.State.ONGOING
        self.save()

    def end(self):
        self.state = Tournament_TextChoices.State.FINISHED
        self.save()

    def add_video(self, video: VideoModel):
        self.videos.add(video)
        participant = GSCParticipant.objects.filter(user=video.player, tournament=self).first()
        if not participant:
            participant = GSCParticipant.objects.create(user=video.player, tournament=self, token=self.token, start_time=datetime.now())

    def refresh_state(self):
        if self.state == Tournament_TextChoices.State.PREPARING and datetime.now() >= self.start_time:
            self.start()
        if self.state == Tournament_TextChoices.State.ONGOING and datetime.now() >= self.end_time:
            self.end()
            return

    def refresh_score(self):
        for video in self.videos.all():
            participant = GSCParticipant.objects.filter(user=video.player, tournament=self).first()
        for participant in GSCParticipant.objects.filter(tournament=self):
            participant.refresh()


class GeneralTournament(Tournament):
    name = models.JSONField()
    description = models.JSONField()
    csv_head = models.JSONField()


class TournamentParticipant(models.Model):
    token = models.CharField(max_length=6) # 比赛标识
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE) # 比赛
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True) # 用户
    start_time = models.DateTimeField(auto_now_add=True) # 参赛时间
    end_time = models.DateTimeField(null=True, blank=True) # 结束时间
    rank = models.PositiveIntegerField(null=True, blank=True) # 排名
    rank_score = models.PositiveSmallIntegerField(default=0) # 比赛积分


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
        models.F('et5sum') + models.F('it12sum') + models.F('bt20sum'),
        output_field=models.PositiveIntegerField(),
        db_persist=True
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

