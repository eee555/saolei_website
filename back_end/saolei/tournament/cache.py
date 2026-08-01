import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime

from django_redis import get_redis_connection

from config.text_choices import Tournament_TextChoices
from utils import ComplexEncoder
from videomanager.models import VideoModel
from .models import GSCTournament, Tournament, TournamentParticipant

cache = get_redis_connection('saolei_website')

NORMAL_TOURNAMENT_CACHE_KEY = 'tournament:normal'
NORMAL_PARTICIPANT_CACHE_KEY = 'tournament:normal:participants'


@dataclass
class CachedNormalTournament:
    id: int
    series: str
    start_time: datetime
    end_time: datetime
    order: int | None = None
    token: str = ''


@dataclass
class CachedNormalParticipant:
    id: int
    token: str
    arbiter_identifier: str | None
    tournament: int
    start_time: datetime
    end_time: datetime


class TournamentCache:
    def update_tournament(self, tournament: Tournament):
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

    def get_tournament(self, tournament_id: int):
        data = cache.hget(NORMAL_TOURNAMENT_CACHE_KEY, tournament_id)
        if data is None:
            return None
        return deserialize_normal_tournament(json.loads(data))

    def get_token_tournament(self, token: str):
        data = self.get_tournament_all()
        return [tournament for tournament in data if tournament.token == token]

    def get_tournament_all(self):
        data = cache.hgetall(NORMAL_TOURNAMENT_CACHE_KEY)
        return [
            deserialize_normal_tournament(json.loads(value))
            for value in data.values()
        ]

    def get_gsc(self):
        data = self.get_tournament_all()
        for tournament in data:
            if tournament.series == Tournament_TextChoices.Series.GSC:
                return tournament
        return None

    def get_participant(self, user_id: int):
        data = cache.hget(NORMAL_PARTICIPANT_CACHE_KEY, user_id)
        if data is None:
            return []
        return [
            deserialize_normal_participant(participant)
            for participant in json.loads(data)
        ]

    def get_arbiter_participant(self, user_id: int, arbiter_identifier: str):
        candidates = self.get_participant(user_id)
        participants = []
        for candidate in candidates:
            if candidate.arbiter_identifier == arbiter_identifier:
                participants.append(candidate)
        return participants

    def get_token_participant(self, user_id: int, tokens: list[str]):
        candidates = self.get_participant(user_id)
        participants = []
        for candidate in candidates:
            if candidate.token in tokens:
                participants.append(candidate)
        return participants

    def checkin_arbiter(self, video: VideoModel, arbiter_identifier: str):
        candidates = self.get_arbiter_participant(video.player_id, arbiter_identifier)
        participants = []
        for candidate in candidates:
            if candidate.start_time <= video.upload_time <= candidate.end_time:
                participants.append(candidate)
        return participants

    def checkin_token(self, video: VideoModel, tokens: list[str]):
        candidates = self.get_token_participant(video.player_id, tokens)
        participants = []
        for candidate in candidates:
            if candidate.start_time <= video.upload_time <= candidate.end_time:
                participants.append(candidate)
        return participants


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
        'id': participant.id,
        'token': participant.token,
        'arbiter_identifier': participant.arbiter_identifier.identifier if participant.arbiter_identifier else None,
        'tournament': participant.tournament_id,
        'start_time': participant.start_time,
        'end_time': participant.end_time,
    }


def deserialize_normal_tournament(data):
    data['start_time'] = _deserialize_datetime(data['start_time'])
    data['end_time'] = _deserialize_datetime(data['end_time'])
    return CachedNormalTournament(**data)


def deserialize_normal_participant(data):
    data['start_time'] = _deserialize_datetime(data['start_time'])
    data['end_time'] = _deserialize_datetime(data['end_time'])
    return CachedNormalParticipant(**data)


def serialize_cached_participant(participant):
    if is_dataclass(participant):
        return asdict(participant)
    return participant


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
    return [
        deserialize_normal_participant(participant)
        for participant in json.loads(cached_data)
    ]


def set_normal_participant_infos_for_user(user_id: int, participants):
    if participants:
        data = [serialize_cached_participant(participant) for participant in participants]
        cache.hset(NORMAL_PARTICIPANT_CACHE_KEY, user_id, json.dumps(data, cls=ComplexEncoder))
    else:
        cache.hdel(NORMAL_PARTICIPANT_CACHE_KEY, user_id)


def upsert_normal_participant_cache(participant: TournamentParticipant):
    if participant.user_id is None:
        return

    participants = [
        cached_participant
        for cached_participant in get_normal_participant_infos_for_user(participant.user_id)
        if cached_participant.tournament != participant.tournament_id
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
        if cached_participant.tournament != participant.tournament_id
    ]
    set_normal_participant_infos_for_user(participant.user_id, participants)
