from django.db.models.signals import post_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .services import update_custom_pluck_rank_for_video


@receiver(post_save, sender=VideoModel, dispatch_uid='customranking.refresh_custom_pluck_rank_on_video_save')
def refresh_custom_pluck_rank_on_video_save(sender, instance: VideoModel, update_fields=None, **kwargs):
    if update_fields is not None:
        update_fields = set(update_fields)
        relevant_fields = {'level', 'mode', 'state', 'ongoing_tournament', 'player', 'timems', 'pluck'}
        if update_fields.isdisjoint(relevant_fields):
            return

    update_custom_pluck_rank_for_video(instance)
