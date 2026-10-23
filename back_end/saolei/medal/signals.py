from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from accountlink.models import AccountLinkQueue, Platform
from tournament.models import TournamentParticipant
from userprofile.models import UserProfile
from videomanager.events import videos_bulk_changed
from videomanager.models import VideoModel
from .cache import invalidate_catalog
from .models import MedalDefinition, MedalGrant, PlayerMedalSummary
from .tasks import enqueue_player_refresh


@receiver(post_save, sender=MedalDefinition)
@receiver(post_delete, sender=MedalDefinition)
def invalidate_medal_catalog(sender, **kwargs):
    invalidate_catalog()


@receiver(pre_delete, sender=VideoModel, dispatch_uid='medal.invalidate_summary_on_video_delete')
@receiver(pre_delete, sender=TournamentParticipant, dispatch_uid='medal.invalidate_summary_on_participant_delete')
@transaction.atomic
def invalidate_summary_on_evidence_delete(sender, instance, **kwargs):
    # SET_NULL 不触发授予的 save；删除前仍能按外键找到受影响的摘要。
    field = 'video' if sender is VideoModel else 'participant'
    player_ids = MedalGrant.objects.filter(**{field: instance}).values_list('user_id', flat=True)
    locked_ids = list(UserProfile.objects.select_for_update().filter(pk__in=player_ids).order_by('pk').values_list('pk', flat=True))
    PlayerMedalSummary.objects.filter(user_id__in=locked_ids).delete()


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
