import json
from datetime import datetime

from django_redis import get_redis_connection

from config.text_choices import Tournament_TextChoices
from utils import ComplexEncoder
from .models import GSCTournament, Tournament, TournamentParticipant

cache = get_redis_connection('saolei_website')

NORMAL_TOURNAMENT_CACHE_KEY = 'tournament:normal'
NORMAL_PARTICIPANT_CACHE_KEY = 'tournament:normal:participants'


class TournamentCache:
    def update_tournament(self, tournament: Tournament):
        tournament = self.select_subclass(tournament)
        if tournament is None:
            return
        if tournament.state == Tournament_TextChoices.State.NORMAL:
            cache.hset(
                NORMAL_TOURNAMENT_CACHE_KEY,
                tournament.id,
                json.dumps(serialize_normal_tournament(tournament), cls=ComplexEncoder),
            )
        else:
            self.remove_tournament(tournament)

    def remove_tournament(self, tournament: Tournament):
        cache.hdel(NORMAL_TOURNAMENT_CACHE_KEY, tournament.id)
        self.remove_tournament_participants(tournament.id)

    def select_subclass(self, tournament: Tournament):
        if type(tournament) is not Tournament:
            return tournament
        return Tournament.objects.filter(id=tournament.id).select_subclasses().first()

    def remove_tournament_participants(self, tournament_id: int):
        pipe = cache.pipeline()
        for user_id, value in cache.hscan_iter(NORMAL_PARTICIPANT_CACHE_KEY):
            participants = [
                participant
                for participant in json.loads(value)
                if participant['tournament'] != tournament_id
            ]
            if participants:
                pipe.hset(
                    NORMAL_PARTICIPANT_CACHE_KEY,
                    user_id,
                    json.dumps(participants, cls=ComplexEncoder),
                )
            else:
                pipe.hdel(NORMAL_PARTICIPANT_CACHE_KEY, user_id)
        pipe.execute()


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


def serialize_normal_participant(participant: TournamentParticipant):
    return {
        'token': participant.token,
        'arbiter_identifier': participant.arbiter_identifier.identifier if participant.arbiter_identifier else None,
        'tournament': participant.tournament_id,
    }


def deserialize_normal_tournament(data):
    data['start_time'] = _deserialize_datetime(data['start_time'])
    data['end_time'] = _deserialize_datetime(data['end_time'])
    return data


def invalidate_normal_participant_cache():
    cache.delete(NORMAL_PARTICIPANT_CACHE_KEY)


def get_normal_tournament_infos():
    cached_data = cache.hgetall(NORMAL_TOURNAMENT_CACHE_KEY)
    return [
        deserialize_normal_tournament(json.loads(value))
        for value in cached_data.values()
    ]


def get_normal_participant_infos_for_user(user_id: int):
    cached_data = cache.hget(NORMAL_PARTICIPANT_CACHE_KEY, user_id)
    if cached_data is None:
        return []
    return json.loads(cached_data)


def set_normal_participant_infos_for_user(user_id: int, participants):
    if participants:
        cache.hset(NORMAL_PARTICIPANT_CACHE_KEY, user_id, json.dumps(participants, cls=ComplexEncoder))
    else:
        cache.hdel(NORMAL_PARTICIPANT_CACHE_KEY, user_id)


def upsert_normal_participant_cache(participant: TournamentParticipant):
    if participant.user_id is None:
        return

    participants = [
        cached_participant
        for cached_participant in get_normal_participant_infos_for_user(participant.user_id)
        if cached_participant['tournament'] != participant.tournament_id
    ]
    if participant.tournament.state == Tournament_TextChoices.State.NORMAL:
        participants.append(serialize_normal_participant(participant))
    set_normal_participant_infos_for_user(participant.user_id, participants)


def delete_normal_participant_cache(participant: TournamentParticipant):
    if participant.user_id is None:
        return

    participants = [
        cached_participant
        for cached_participant in get_normal_participant_infos_for_user(participant.user_id)
        if cached_participant['tournament'] != participant.tournament_id
    ]
    set_normal_participant_infos_for_user(participant.user_id, participants)


def get_normal_participant_info_by_arbiter_identifier(user_id: int, arbiter_identifier: str):
    for participant in get_normal_participant_infos_for_user(user_id):
        if participant['arbiter_identifier'] == arbiter_identifier:
            return participant
    return None


def get_normal_participant_info_by_tournament(user_id: int, tournament_id: int):
    for participant in get_normal_participant_infos_for_user(user_id):
        if participant['tournament'] == tournament_id:
            return participant
    return None


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
