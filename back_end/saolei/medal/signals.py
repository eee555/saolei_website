from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from accountlink.models import AccountLinkQueue, Platform
from userprofile.models import UserProfile
from videomanager.events import videos_bulk_changed
from videomanager.models import VideoModel
from .cache import invalidate_catalog
from .models import MedalDefinition
from .tasks import enqueue_player_refresh


@receiver(post_save, sender=MedalDefinition)
@receiver(post_delete, sender=MedalDefinition)
def invalidate_medal_catalog(sender, **kwargs):
    invalidate_catalog()


def _enqueue_video_players(instance):
    player_ids = []
    current = getattr(instance, 'player_id', None)
    if current:
        player_ids.append(current)
    old_values = getattr(instance, '_old_values', None) or {}
    previous = old_values.get('player_id')
    if previous and previous not in player_ids:
        player_ids.append(previous)
    for player_id in player_ids:
        transaction.on_commit(lambda player_id=player_id: enqueue_player_refresh(player_id))


@receiver(post_save, sender=VideoModel, dispatch_uid='medal.refresh_on_video_save')
@receiver(post_delete, sender=VideoModel, dispatch_uid='medal.refresh_on_video_delete')
def enqueue_medal_refresh_on_video(sender, instance, **kwargs):
    _enqueue_video_players(instance)


@receiver(videos_bulk_changed, dispatch_uid='medal.refresh_on_videos_bulk_changed')
def enqueue_medal_refresh_on_bulk_videos(sender, player_ids, **kwargs):
    for player_id in sorted(set(player_ids) - {None}):
        transaction.on_commit(lambda player_id=player_id: enqueue_player_refresh(player_id), robust=True)


@receiver(post_save, sender=UserProfile, dispatch_uid='medal.refresh_on_profile_save')
def enqueue_medal_refresh_on_profile(sender, instance, created=False, update_fields=None, **kwargs):
    if update_fields is not None and '_realname' not in update_fields:
        return
    if created and instance.realname == '匿名':
        return
    user_id = instance.pk
    if not user_id:
        return
    transaction.on_commit(lambda user_id=user_id: enqueue_player_refresh(user_id))


@receiver(post_save, sender=AccountLinkQueue, dispatch_uid='medal.refresh_on_saolei_link_save')
@receiver(post_delete, sender=AccountLinkQueue, dispatch_uid='medal.refresh_on_saolei_link_delete')
def enqueue_medal_refresh_on_saolei_link(sender, instance, **kwargs):
    if instance.platform != Platform.SAOLEI:
        return
    user_id = instance.userprofile_id
    if not user_id:
        return
    transaction.on_commit(lambda user_id=user_id: enqueue_player_refresh(user_id))
