from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .cache import (
    TournamentCache,
    delete_normal_participant_cache,
    upsert_normal_participant_cache,
)
from .models import GSCParticipant, GSCTournament, Tournament, TournamentParticipant, select_tournament_subclass
from .services import add_existing_videos_to_participant_tournament
from .utils import add_video_to_checked_tournaments, video_checkin

cache = TournamentCache()


def update_tournament_cache(instance: Tournament):
    tournament = select_tournament_subclass(instance)
    if tournament is not None:
        cache.update_tournament(tournament)


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


@receiver(post_save, sender=Tournament, dispatch_uid='tournament.invalidate_normal_cache_on_tournament_save')
def invalidate_normal_cache_on_tournament_save(sender, instance: Tournament, **kwargs):
    transaction.on_commit(lambda: update_tournament_cache(instance))


@receiver(post_delete, sender=Tournament, dispatch_uid='tournament.invalidate_normal_cache_on_tournament_delete')
def invalidate_normal_cache_on_tournament_delete(sender, instance: Tournament, **kwargs):
    transaction.on_commit(lambda: cache.remove_tournament(select_tournament_subclass(instance) or instance))


@receiver(post_save, sender=GSCTournament, dispatch_uid='tournament.invalidate_normal_cache_on_gsc_save')
def invalidate_normal_cache_on_gsc_save(sender, instance: GSCTournament, **kwargs):
    transaction.on_commit(lambda: cache.update_tournament(instance))


@receiver(post_delete, sender=GSCTournament, dispatch_uid='tournament.invalidate_normal_cache_on_gsc_delete')
def invalidate_normal_cache_on_gsc_delete(sender, instance: GSCTournament, **kwargs):
    transaction.on_commit(lambda: cache.remove_tournament(instance))


@receiver(post_save, sender=TournamentParticipant, dispatch_uid='tournament.rebuild_normal_participant_cache_on_save')
def rebuild_normal_participant_cache_on_save(sender, instance: TournamentParticipant, created: bool, **kwargs):
    transaction.on_commit(lambda: upsert_normal_participant_cache(instance))
    if created:
        transaction.on_commit(lambda: add_existing_videos_to_participant_tournament(instance))


@receiver(post_delete, sender=TournamentParticipant, dispatch_uid='tournament.rebuild_normal_participant_cache_on_delete')
def rebuild_normal_participant_cache_on_delete(sender, instance: TournamentParticipant, **kwargs):
    transaction.on_commit(lambda: delete_normal_participant_cache(instance))


@receiver(post_save, sender=GSCParticipant, dispatch_uid='tournament.rebuild_normal_gsc_participant_cache_on_save')
def rebuild_normal_gsc_participant_cache_on_save(sender, instance: GSCParticipant, created: bool, **kwargs):
    transaction.on_commit(lambda: upsert_normal_participant_cache(instance))
    if created:
        transaction.on_commit(lambda: add_existing_videos_to_participant_tournament(instance))


@receiver(post_delete, sender=GSCParticipant, dispatch_uid='tournament.rebuild_normal_gsc_participant_cache_on_delete')
def rebuild_normal_gsc_participant_cache_on_delete(sender, instance: GSCParticipant, **kwargs):
    transaction.on_commit(lambda: delete_normal_participant_cache(instance))
