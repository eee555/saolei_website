from django.db import models

from config.global_settings import MaxSizes
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import VideoModel


class CustomPluckRecord(models.Model):
    player = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE)
    level = models.CharField(max_length=MaxSizes.GAMELEVEL, choices=MS_TextChoices.Level.choices)
    mode = models.CharField(max_length=MaxSizes.GAMEMODE, choices=MS_TextChoices.Mode.choices)
    pluck = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['player', 'level'], name='custom_pluck_player_board_uniq'),
        ]
        indexes = [
            models.Index(fields=['level', 'pluck'], name='custom_pluck_rank_idx'),
            models.Index(fields=['video'], name='custom_pluck_video_idx'),
        ]
