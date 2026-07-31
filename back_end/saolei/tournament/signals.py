from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .cache import invalidate_normal_tournament_cache
from .models import GSCTournament, Tournament
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


def invalidate_normal_tournament_cache_on_commit():
    transaction.on_commit(invalidate_normal_tournament_cache)


@receiver(post_save, sender=Tournament, dispatch_uid='tournament.invalidate_normal_cache_on_tournament_save')
def invalidate_normal_cache_on_tournament_save(sender, instance: Tournament, **kwargs):
    invalidate_normal_tournament_cache_on_commit()


@receiver(post_delete, sender=Tournament, dispatch_uid='tournament.invalidate_normal_cache_on_tournament_delete')
def invalidate_normal_cache_on_tournament_delete(sender, instance: Tournament, **kwargs):
    invalidate_normal_tournament_cache_on_commit()


@receiver(post_save, sender=GSCTournament, dispatch_uid='tournament.invalidate_normal_cache_on_gsc_save')
def invalidate_normal_cache_on_gsc_save(sender, instance: GSCTournament, **kwargs):
    invalidate_normal_tournament_cache_on_commit()


@receiver(post_delete, sender=GSCTournament, dispatch_uid='tournament.invalidate_normal_cache_on_gsc_delete')
def invalidate_normal_cache_on_gsc_delete(sender, instance: GSCTournament, **kwargs):
    invalidate_normal_tournament_cache_on_commit()
