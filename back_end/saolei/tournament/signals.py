from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from videomanager.models import VideoModel
from .cache import invalidate_normal_tournament_cache, rebuild_normal_participants_for_user
from .models import GSCParticipant, GSCTournament, Tournament, TournamentParticipant
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


def rebuild_normal_participant_cache_on_commit(user_id):
    if user_id is None:
        return
    transaction.on_commit(lambda: rebuild_normal_participants_for_user(user_id))


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


@receiver(post_save, sender=TournamentParticipant, dispatch_uid='tournament.rebuild_normal_participant_cache_on_save')
def rebuild_normal_participant_cache_on_save(sender, instance: TournamentParticipant, **kwargs):
    rebuild_normal_participant_cache_on_commit(instance.user_id)


@receiver(post_delete, sender=TournamentParticipant, dispatch_uid='tournament.rebuild_normal_participant_cache_on_delete')
def rebuild_normal_participant_cache_on_delete(sender, instance: TournamentParticipant, **kwargs):
    rebuild_normal_participant_cache_on_commit(instance.user_id)


@receiver(post_save, sender=GSCParticipant, dispatch_uid='tournament.rebuild_normal_gsc_participant_cache_on_save')
def rebuild_normal_gsc_participant_cache_on_save(sender, instance: GSCParticipant, **kwargs):
    rebuild_normal_participant_cache_on_commit(instance.user_id)


@receiver(post_delete, sender=GSCParticipant, dispatch_uid='tournament.rebuild_normal_gsc_participant_cache_on_delete')
def rebuild_normal_gsc_participant_cache_on_delete(sender, instance: GSCParticipant, **kwargs):
    rebuild_normal_participant_cache_on_commit(instance.user_id)
