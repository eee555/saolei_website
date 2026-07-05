from django.db import models

from config.global_settings import MaxSizes
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import VideoModel


class CustomPluckRecord(models.Model):
    player = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE)
    level = models.CharField(max_length=MaxSizes.GAMELEVEL, choices=MS_TextChoices.Level.choices)
    pluck = models.FloatField()
    timems = models.IntegerField()
    upload_time = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['player', 'level'], name='custom_pluck_player_board_uniq'),
        ]
        indexes = [
            models.Index(fields=['level', 'pluck'], name='custom_pluck_rank_idx'),
            models.Index(fields=['video'], name='custom_pluck_video_idx'),
        ]

    def add_video(self, video: VideoModel):
        """如果录像优于当前纪录，则替换当前纪录并返回 True。"""
        if video.pluck is None:
            return False
        if (video.pluck, video.timems, video.upload_time) >= (self.pluck, self.timems, self.upload_time):
            return False

        self.video = video
        self.pluck = video.pluck
        self.timems = video.timems
        self.upload_time = video.upload_time
        self.save(update_fields=['video', 'pluck', 'timems', 'upload_time', 'updated_at'])
        return True
