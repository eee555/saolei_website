from django.db.models.signals import post_save
from django.dispatch import receiver

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel
from videomanager.utils import is_custom_pluck_video
from .services import add_to_custom_pluck_rank, remove_from_custom_pluck_rank


def can_join_custom_pluck_rank(video: VideoModel) -> bool:
    return (
        is_custom_pluck_video(video)
        and video.state == MS_TextChoices.State.OFFICIAL
        and not video.ongoing_tournament
        and video.pluck is not None
    )


@receiver(post_save, sender=VideoModel, dispatch_uid='customranking.refresh_custom_pluck_rank_on_video_save')
def refresh_custom_pluck_rank_on_video_save(sender, instance: VideoModel, update_fields=None, **kwargs):
    if update_fields is not None:
        update_fields = set(update_fields)
        should_refresh = (
            'ongoing_tournament' in update_fields
            or ('pluck' in update_fields and not instance.ongoing_tournament)
            or (
                'state' in update_fields
                and instance.state == MS_TextChoices.State.OFFICIAL
                and not instance.ongoing_tournament
            )
        )
        if not should_refresh:
            return

    if can_join_custom_pluck_rank(instance):
        add_to_custom_pluck_rank(instance)
    else:
        remove_from_custom_pluck_rank(instance)
