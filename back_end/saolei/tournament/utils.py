from django.utils import timezone

from .models import Tournament


def tournament_accepts_checkin(tournament: Tournament):
    now = timezone.now()
    return (
        tournament.start_time is not None
        and tournament.end_time is not None
        and tournament.start_time <= now < tournament.end_time
    )


def tournament_has_ended(tournament: Tournament):
    return tournament.end_time is not None and timezone.now() >= tournament.end_time
