from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from tournament.cache import TournamentCache
from .services import calculate_weekly_classic_best, update_weekly_best
from ..models import TournamentUser, WeeklyParticipant

tournament_cache = TournamentCache()

WEEKLY_BEST_SCORE_FIELDS = {
    'classic_score',
}


def weekly_best_score_fields_changed(update_fields):
    return update_fields is None or bool(WEEKLY_BEST_SCORE_FIELDS.intersection(update_fields))


@receiver(post_save, sender=WeeklyParticipant, dispatch_uid='tournament.update_best_score_on_weekly_participant_save')
def update_best_score_on_weekly_participant_save(sender, instance: WeeklyParticipant, created: bool, update_fields=None, **kwargs):
    if instance.user_id is None or not weekly_best_score_fields_changed(update_fields):
        return
    tournament_user, _ = TournamentUser.objects.get_or_create(user_id=instance.user_id)
    if update_weekly_best(tournament_user, instance.tournament.weeklytournament, instance):
        tournament_user.save(update_fields=['weekly_classic_best'])
        tournament_cache.update_tournament_user(tournament_user, fields=['weekly_classic_best'])


@receiver(post_delete, sender=WeeklyParticipant, dispatch_uid='tournament.update_best_score_on_weekly_participant_delete')
def update_best_score_on_weekly_participant_delete(sender, instance: WeeklyParticipant, **kwargs):
    if instance.user_id is None:
        return
    tournament_user: TournamentUser = instance.user.tournamentuser
    tournament_user.weekly_classic_best = calculate_weekly_classic_best(instance.user_id)
    tournament_user.save(update_fields=['weekly_classic_best'])
    tournament_cache.update_tournament_user(tournament_user, fields=['weekly_classic_best'])
