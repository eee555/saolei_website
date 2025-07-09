import string
import secrets
from django.db import models
from userprofile.models import UserProfile
from config.text_choices import Tournament_TextChoices

def generate_random_token(length=4):
    """生成指定位数的随机字母数字混合码"""
    alphabet = string.ascii_letters + string.digits  # 大小写字母+数字
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class Tournament(models.Model):
    start_time = models.DateTimeField() # 比赛开始时间
    end_time = models.DateTimeField() # 比赛结束时间
    state = models.CharField(max_length=1, choices=Tournament_TextChoices.State.choices, default=Tournament_TextChoices.State.PENDING) # 比赛状态
    host = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True) # 主办方
    weight = models.PositiveIntegerField(default=0) # 比赛总积分

class GSCTournament(Tournament):
    pass

class GeneralTournament(Tournament):
    name = models.JSONField()
    description = models.JSONField()
    csv_head = models.JSONField()


class TournamentParticipant(models.Model):
    token = models.CharField(max_length=4, unique=True) # 比赛标识
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

class GSCParticipant(TournamentParticipant):
    bt1st = models.PositiveIntegerField(default=10000)
    bt20th = models.PositiveIntegerField(default=10000)
    bt20sum = models.PositiveIntegerField(default=200000)

    it1st = models.PositiveIntegerField(default=60000)
    it12th = models.PositiveIntegerField(default=60000)
    it12sum = models.PositiveIntegerField(default=720000)

    et1st = models.PositiveIntegerField(default=240000)
    et5th = models.PositiveIntegerField(default=240000)
    et5sum = models.PositiveIntegerField(default=1200000)

    t37 = models.GeneratedField(
        models.F('et5sum') + models.F('it12sum') + models.F('bt20sum'),
        output_field=models.PositiveIntegerField(),
        db_persist=True
    )

class TournamentVideo(models.Model):
    participant = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE)
    video = models.ForeignKey('videomanager.VideoModel', on_delete=models.CASCADE)

