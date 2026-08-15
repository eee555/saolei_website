from dataclasses import dataclass
from datetime import datetime
import json
from typing import Literal

from dataclasses_json import dataclass_json
from django_redis import get_redis_connection

from config.text_choices import Tournament_TextChoices
from utils.cache import maybe_bytes_to_str
from videomanager.models import VideoModel
from .models import GSCTournament, Tournament, TournamentParticipant

cache = get_redis_connection('saolei_website')

NORMAL_TOURNAMENT_CACHE_KEY = 'tournament:normal'
NORMAL_PARTICIPANT_CACHE_KEY = 'tournament:normal:participants'


@dataclass_json
@dataclass
class CachedTournament:
    id: int
    state: Tournament_TextChoices.State
    subclass: Tournament_TextChoices.Subclass
    host_id: int | None
    start_time: datetime
    end_time: datetime


@dataclass_json
@dataclass
class CachedGSCTournamentData:
    order: int
    token: str


@dataclass_json
@dataclass
class CachedWeeklyTournamentData:
    year: int
    week: int
    tournament_format: str


@dataclass_json
@dataclass
class CachedGSCTournament(CachedTournament):
    subclass: Literal[Tournament_TextChoices.Subclass.GSC]
    data: CachedGSCTournamentData


@dataclass_json
@dataclass
class CachedWeeklyTournament(CachedTournament):
    subclass: Literal[Tournament_TextChoices.Subclass.WEEKLY]
    data: CachedWeeklyTournamentData


@dataclass_json
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
        tournament = tournament.select_subclass()
        if tournament.state == Tournament_TextChoices.State.NORMAL:
            cache.hset(
                NORMAL_TOURNAMENT_CACHE_KEY,
                tournament.id,
                serialize_normal_tournament(tournament).to_json(),
            )
        else:
            self.remove_tournament(tournament.id)

    def remove_tournament(self, tournament_id: int):
        cache.hdel(NORMAL_TOURNAMENT_CACHE_KEY, tournament_id)
        self.remove_tournament_participants(tournament_id)

    def remove_tournament_participants(self, tournament_id: int):
        pipe = cache.pipeline()
        for user_id, value in cache.hscan_iter(NORMAL_PARTICIPANT_CACHE_KEY):
            participants = [
                participant
                for participant in CachedNormalParticipant.schema().loads(value, many=True)
                if participant.tournament != tournament_id
            ]
            if participants:
                pipe.hset(
                    NORMAL_PARTICIPANT_CACHE_KEY,
                    user_id,
                    CachedNormalParticipant.schema().dumps(participants, many=True),
                )
            else:
                pipe.hdel(NORMAL_PARTICIPANT_CACHE_KEY, user_id)
        pipe.execute()

    def get_tournament(self, tournament_id: int):
        data = cache.hget(NORMAL_TOURNAMENT_CACHE_KEY, tournament_id)
        if data is None:
            return None
        return deserialize_cached_tournament(data)

    def get_tournament_all(self):
        data = cache.hgetall(NORMAL_TOURNAMENT_CACHE_KEY)
        return [
            deserialize_cached_tournament(value)
            for value in data.values()
        ]

    def get_gsc(self):
        data = self.get_tournament_all()
        for tournament in data:
            if tournament.subclass == Tournament_TextChoices.Subclass.GSC:
                return tournament
        return None

    def get_participant_list(self, user_id: int) -> list[CachedNormalParticipant]:
        data = cache.hget(NORMAL_PARTICIPANT_CACHE_KEY, user_id)
        if data is None:
            return []
        return CachedNormalParticipant.schema().loads(data, many=True)

    def set_participant_list(self, user_id: int, participants: list[CachedNormalParticipant]):
        if participants:
            cache.hset(NORMAL_PARTICIPANT_CACHE_KEY, user_id, CachedNormalParticipant.schema().dumps(participants, many=True))
        else:
            cache.hdel(NORMAL_PARTICIPANT_CACHE_KEY, user_id)

    def remove_participant(self, user_id: int, tournament_id: int):
        participants = [
            cached_participant
            for cached_participant in self.get_participant_list(user_id)
            if cached_participant.tournament != tournament_id
        ]
        self.set_participant_list(user_id, participants)

    def update_participant(self, participant: TournamentParticipant):
        participants = [
            cached_participant
            for cached_participant in self.get_participant_list(participant.user_id)
            if cached_participant.tournament != participant.tournament_id
        ]
        if participant.tournament.state == Tournament_TextChoices.State.NORMAL:
            participants.append(serialize_normal_participant(participant))
        self.set_participant_list(participant.user_id, participants)

    def checkin_arbiter(self, video: VideoModel, arbiter_identifier: str) -> list[CachedNormalParticipant]:
        return [
            participant
            for participant in self.get_participant_list(video.player_id)
            if (
                participant.arbiter_identifier == arbiter_identifier
                and participant.start_time <= video.upload_time <= participant.end_time
            )
        ]

    def checkin_token(self, video: VideoModel, tokens: list[str]) -> list[CachedNormalParticipant]:
        return [
            participant
            for participant in self.get_participant_list(video.player_id)
            if (
                participant.token in tokens
                and participant.start_time <= video.upload_time <= participant.end_time
            )
        ]


def serialize_normal_tournament(tournament: Tournament):
    if isinstance(tournament, GSCTournament):
        return CachedGSCTournament(
            id=tournament.id,
            state=tournament.state,
            subclass=Tournament_TextChoices.Subclass.GSC,
            host_id=tournament.host_id,
            start_time=tournament.start_time,
            end_time=tournament.end_time,
            data=CachedGSCTournamentData(
                order=tournament.order,
                token=tournament.token,
            ),
        )
    return CachedWeeklyTournament(
        id=tournament.id,
        state=tournament.state,
        subclass=Tournament_TextChoices.Subclass.WEEKLY,
        host_id=tournament.host_id,
        start_time=tournament.start_time,
        end_time=tournament.end_time,
        data=CachedWeeklyTournamentData(
            year=tournament.year,
            week=tournament.week,
            tournament_format=tournament.tournament_format,
        ),
    )


def deserialize_cached_tournament(value):
    json_value = maybe_bytes_to_str(value)
    raw_value = json.loads(json_value)
    if raw_value['subclass'] == Tournament_TextChoices.Subclass.GSC:
        return CachedGSCTournament.from_json(json_value)
    return CachedWeeklyTournament.from_json(json_value)


def serialize_normal_participant(participant: TournamentParticipant):
    return CachedNormalParticipant(
        id=participant.id,
        token=participant.token,
        arbiter_identifier=participant.arbiter_identifier.identifier if participant.arbiter_identifier else None,
        tournament=participant.tournament_id,
        start_time=participant.start_time,
        end_time=participant.end_time,
    )


def invalidate_normal_participant_cache():
    cache.delete(NORMAL_PARTICIPANT_CACHE_KEY)
