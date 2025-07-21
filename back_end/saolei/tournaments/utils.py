from datetime import datetime
from config.text_choices import Tournament_TextChoices
from .models import Tournament

def refresh_tournament(tournament: Tournament):
    if tournament.state == Tournament_TextChoices.State.PREPARING:
        if datetime.now() >= tournament.start_time:
            tournament.state = Tournament_TextChoices.State.ONGOING
            tournament.save()
    elif tournament.state == Tournament_TextChoices.State.ONGOING:
        if datetime.now() >= tournament.end_time:
            tournament.state = Tournament_TextChoices.State.FINISHED
            tournament.save()
    elif tournament.state == Tournament_TextChoices.State.PENDING:
        if datetime.now() >= tournament.start_time:
            tournament.state = Tournament_TextChoices.State.CANCELLED
            tournament.save()
    return tournament

def finish_tournament(tournament: Tournament):
    if tournament.series == Tournament_TextChoices.Series.GSC:
        pass
    elif tournament.series == Tournament_TextChoices.Series.WEEKLY:
        pass
    tournament.state = Tournament_TextChoices.State.FINISHED

