from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel
from .models import Identifier


def mark_identifier_videos_official(identifier: Identifier):
    if not identifier.safe or identifier.userms_id is None:
        return

    videos = VideoModel.objects.filter(
        player__userms_id=identifier.userms_id,
        video__identifier=identifier.identifier,
        state=MS_TextChoices.State.IDENTIFIER,
    )
    for video in videos:
        video.state = MS_TextChoices.State.OFFICIAL
        video.save(update_fields=['state'])


def mark_identifier_videos_unmatched(identifier_text: str, userms_id: int | None):
    if userms_id is None:
        return

    videos = VideoModel.objects.filter(
        player__userms_id=userms_id,
        video__identifier=identifier_text,
        state=MS_TextChoices.State.OFFICIAL,
    )
    for video in videos:
        video.state = MS_TextChoices.State.IDENTIFIER
        video.save(update_fields=['state'])


@receiver(pre_save, sender=Identifier, dispatch_uid='identifier.capture_previous_identifier_state')
def capture_previous_identifier_state(sender, instance: Identifier, **kwargs):
    if instance.pk is None:
        instance._previous_identifier = None
        return

    instance._previous_identifier = (
        Identifier.objects
        .filter(pk=instance.pk)
        .values('identifier', 'userms_id', 'safe')
        .first()
    )


@receiver(post_save, sender=Identifier, dispatch_uid='identifier.refresh_video_state_on_identifier_save')
def refresh_video_state_on_identifier_save(sender, instance: Identifier, **kwargs):
    previous = getattr(instance, '_previous_identifier', None)
    previous_identifier = previous['identifier'] if previous else instance.identifier
    previous_userms_id = previous['userms_id'] if previous else None
    previous_safe = previous['safe'] if previous else False

    if previous_safe and (
        previous_userms_id != instance.userms_id
        or previous_identifier != instance.identifier
    ):
        mark_identifier_videos_unmatched(previous_identifier, previous_userms_id)
    elif previous_safe and not instance.safe:
        mark_identifier_videos_unmatched(previous_identifier, previous_userms_id)

    mark_identifier_videos_official(instance)


@receiver(post_delete, sender=Identifier, dispatch_uid='identifier.refresh_video_state_on_identifier_delete')
def refresh_video_state_on_identifier_delete(sender, instance: Identifier, **kwargs):
    mark_identifier_videos_unmatched(instance.identifier, instance.userms_id)
