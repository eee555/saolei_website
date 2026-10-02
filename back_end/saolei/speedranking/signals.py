from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from videomanager.signals import field_changed
from .services import sync_video

RANKING_FIELDS = {'player_id', 'level', 'mode', 'state', 'ongoing_tournament', 'bv', 'timems', 'right_ce', 'upload_time'}


@receiver(post_save, sender=VideoModel, dispatch_uid='speedranking.video_saved')
def refresh_ranks_on_video_save(sender, instance: VideoModel, created, raw=False, **kwargs):
    if raw:
        return
    if not created and not any(field_changed(instance, field) for field in RANKING_FIELDS):
        return
    old_player = getattr(instance, '_old_values', {}).get('player_id', instance.player_id)
    sync_video(instance.pk, old_player)


@receiver(post_delete, sender=VideoModel, dispatch_uid='speedranking.video_deleted')
def refresh_ranks_on_video_delete(sender, instance: VideoModel, **kwargs):
    sync_video(instance.pk, instance.player_id)
