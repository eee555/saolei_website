
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from tournament.cache import TournamentCache
from .services import calculate_gsc_best_score, update_gsc_best
from ..models import GSCParticipant, TournamentUser

tournament_cache = TournamentCache()

GSC_BEST_SCORE_FIELDS = {
    'bt20sum',
    'it12sum',
    'et5sum',
}


def gsc_best_score_fields_changed(update_fields):
    return update_fields is None or bool(GSC_BEST_SCORE_FIELDS.intersection(update_fields))


@receiver(post_save, sender=GSCParticipant, dispatch_uid='tournament.update_best_score_on_gsc_participant_save')
def update_best_score_on_gsc_participant_save(sender, instance: GSCParticipant, created: bool, update_fields=None, **kwargs):
    if instance.user_id is None or not gsc_best_score_fields_changed(update_fields):
        return
    tournament_user, _ = TournamentUser.objects.get_or_create(user_id=instance.user_id)
    if update_gsc_best(tournament_user, instance.tournament.gsctournament, instance):
        tournament_user.save(update_fields=['gsc_best'])
        tournament_cache.update_tournament_user(tournament_user, fields=['gsc_best'])


@receiver(post_delete, sender=GSCParticipant, dispatch_uid='tournament.update_best_score_on_gsc_participant_delete')
def update_best_score_on_gsc_participant_delete(sender, instance: GSCParticipant, **kwargs):
    if instance.user_id is None:
        return
    tournament_user: TournamentUser = instance.user.tournamentuser
    tournament_user.gsc_best = calculate_gsc_best_score(instance.user_id)
    tournament_user.save(update_fields=['gsc_best'])
    tournament_cache.update_tournament_user(tournament_user, fields=['gsc_best'])
