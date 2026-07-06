from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .services import can_update_personal_record, should_rebuild_personal_record, update_personal_record, update_personal_record_stock

PERSONAL_RECORD_RELATED_VIDEO_FIELDS = {
    'state',
    'ongoing_tournament',
    'player',
    'player_id',
    'level',
    'mode',
    'timems',
    'bv',
    'path',
}


@receiver(pre_save, sender=VideoModel, dispatch_uid='msuser.capture_previous_video_for_personal_record')
def capture_previous_video_for_personal_record(sender, instance: VideoModel, update_fields=None, **kwargs):
    if instance.pk is None:
        instance._msuser_previous_video = None
        return
    if update_fields is not None and not (set(update_fields) & PERSONAL_RECORD_RELATED_VIDEO_FIELDS):
        instance._msuser_previous_video = None
        return
    instance._msuser_previous_video = (
        VideoModel.objects
        .select_related('player__userms', 'video')
        .filter(pk=instance.pk)
        .first()
    )


@receiver(post_save, sender=VideoModel, dispatch_uid='msuser.refresh_personal_record_on_video_save')
def refresh_personal_record_on_video_save(sender, instance: VideoModel, created: bool, update_fields=None, **kwargs):
    if created or getattr(instance, '_skip_msuser_ranking_signal', False):
        return
    if update_fields is not None and not (set(update_fields) & PERSONAL_RECORD_RELATED_VIDEO_FIELDS):
        return

    previous_video = getattr(instance, '_msuser_previous_video', None)
    previous_can_rank = previous_video is not None and can_update_personal_record(previous_video)
    current_can_rank = can_update_personal_record(instance)

    if current_can_rank and previous_can_rank:
        if should_rebuild_personal_record(instance, previous_video):
            update_personal_record_stock(previous_video.player)
            if previous_video.player_id != instance.player_id:
                update_personal_record_stock(instance.player)
        else:
            update_personal_record(instance)
    elif current_can_rank:
        update_personal_record(instance)
    elif previous_can_rank:
        update_personal_record_stock(previous_video.player)
