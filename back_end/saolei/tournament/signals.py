from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .utils import add_video_to_checked_tournaments, video_checkin


@receiver(pre_save, sender=VideoModel, dispatch_uid='tournament.checkin_video_before_create')
def checkin_video_before_create(sender, instance: VideoModel, **kwargs):
    if instance.pk is not None:
        return
    video_checkin(instance, getattr(instance, '_tournament_identifiers', []))


@receiver(post_save, sender=VideoModel, dispatch_uid='tournament.add_created_video_to_checked_tournaments')
def add_created_video_to_checked_tournaments(sender, instance: VideoModel, created: bool, **kwargs):
    if not created:
        return
    add_video_to_checked_tournaments(instance)
