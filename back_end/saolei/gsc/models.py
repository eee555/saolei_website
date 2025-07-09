
from django.db import models
from videomanager.models import VideoModel
from userprofile.models import UserProfile
from config.text_choices import MS_TextChoices


class GSC(models.Model):
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    token = models.CharField(max_length=6, unique=True)

class GSCParticipant(models.Model):
    gsc = models.ForeignKey(GSC, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

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


class GSCVideo(models.Model):
    participant = models.ForeignKey(GSCParticipant, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE)
    level = models.CharField(max_length=1, choices=MS_TextChoices.Level.choices)
    timems = models.PositiveIntegerField()
    bv = models.PositiveSmallIntegerField()

    def create(self, *args, **kwargs):
        """创建GSC视频时自动计算qg"""
        self.level = self.video.level
        self.timems = self.video.timems
        self.bv = self.video.bv



    