import json
from datetime import datetime

from django_redis import get_redis_connection

from config.text_choices import Tournament_TextChoices
from utils import ComplexEncoder
from .models import GSCTournament, Tournament

cache = get_redis_connection('saolei_website')

NORMAL_TOURNAMENT_CACHE_KEY = 'tournament:normal'


def _deserialize_datetime(value):
    if value is None:
        return None
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def serialize_normal_tournament(tournament: Tournament):
    data = {
        'id': tournament.id,
        'series': tournament.series,
        'start_time': tournament.start_time,
        'end_time': tournament.end_time,
    }
    if isinstance(tournament, GSCTournament):
        data['order'] = tournament.order
        data['token'] = tournament.token
    return data


def deserialize_normal_tournament(data):
    data['start_time'] = _deserialize_datetime(data['start_time'])
    data['end_time'] = _deserialize_datetime(data['end_time'])
    return data


def invalidate_normal_tournament_cache():
    cache.delete(NORMAL_TOURNAMENT_CACHE_KEY)


def rebuild_normal_tournament_cache():
    tournaments = Tournament.objects.filter(state=Tournament_TextChoices.State.NORMAL).select_subclasses()
    data = [serialize_normal_tournament(tournament) for tournament in tournaments]
    mapping = {
        tournament['id']: json.dumps(tournament, cls=ComplexEncoder)
        for tournament in data
    }

    cache.delete(NORMAL_TOURNAMENT_CACHE_KEY)
    if mapping:
        cache.hset(NORMAL_TOURNAMENT_CACHE_KEY, mapping=mapping)

    return data


def get_normal_tournament_infos():
    cached_data = cache.hgetall(NORMAL_TOURNAMENT_CACHE_KEY)
    if not cached_data:
        return rebuild_normal_tournament_cache()

    return [
        deserialize_normal_tournament(json.loads(value))
        for value in cached_data.values()
    ]


def get_normal_gsc_tournament_info():
    for tournament in get_normal_tournament_infos():
        if tournament['series'] == Tournament_TextChoices.Series.GSC:
            return tournament
    return None


def normal_tournament_accepts_checkin(tournament):
    from django.utils import timezone

    now = timezone.now()
    return (
        tournament['start_time'] is not None
        and tournament['end_time'] is not None
        and tournament['start_time'] <= now < tournament['end_time']
    )


def get_normal_gsc_tournament_by_token(token: str):
    tournament = get_normal_gsc_tournament_info()
    if tournament is None:
        return None
    if tournament.get('token') != token or not normal_tournament_accepts_checkin(tournament):
        return None
    return GSCTournament.objects.filter(order=tournament['order'], token=token).first()
