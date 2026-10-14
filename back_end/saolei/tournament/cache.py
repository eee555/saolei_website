from dataclasses import dataclass
from datetime import datetime
import json
from typing import Iterable, Literal

from dataclasses_json import dataclass_json
from django.db.models import Max
from django_redis import get_redis_connection

from config.text_choices import Tournament_TextChoices
from utils.cache import maybe_bytes_to_str
from videomanager.models import VideoModel
from .models import GSCTournament, Tournament, TournamentParticipant, TournamentUser
from .utils import MAX_TOURNAMENT_BEST, tournament_score_decay_factor

cache = get_redis_connection('saolei_website')

NORMAL_TOURNAMENT_CACHE_KEY = 'tournament:normal'
NORMAL_PARTICIPANT_CACHE_KEY = 'tournament:normal:participants'
TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY = 'tournament:user:score_current:last_updated'

TOURNAMENT_USER_CACHE_KEYS = {
    'score_current': 'tournament:user:score_current',
    'score_total': 'tournament:user:score_total',
    'gsc_total': 'tournament:user:gsc_total',
    'gsc_best': 'tournament:user:gsc_best',
    'weekly_total': 'tournament:user:weekly_total',
    'weekly_classic_total': 'tournament:user:weekly_classic_total',
    'weekly_classic_best': 'tournament:user:weekly_classic_best',
}
TOURNAMENT_USER_RANK_FIELDS = (
    'score_current', 'score_total',
    'gsc_total', 'gsc_best',
    'weekly_total', 'weekly_classic_total', 'weekly_classic_best',
)
TOURNAMENT_USER_ASC_FIELDS = ('gsc_best', 'weekly_classic_best')
TOURNAMENT_USER_DEFAULT_VALUES = {
    'score_current': 0,
    'score_total': 0,
    'gsc_total': 0,
    'gsc_best': MAX_TOURNAMENT_BEST,
    'weekly_total': 0,
    'weekly_classic_total': 0,
    'weekly_classic_best': MAX_TOURNAMENT_BEST,
}


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

    def clear_tournament_user_cache(self):
        cache.delete(*TOURNAMENT_USER_CACHE_KEYS.values(), TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY)

    def update_tournament_user(self, tournament_user: TournamentUser, fields=None):
        self.update_tournament_users([tournament_user], fields=fields)

    def update_tournament_users(self, tournament_users: Iterable[TournamentUser], fields=None):
        fields = self._normalize_tournament_user_fields(fields)
        if not fields:
            return
        # 事务可能因并发修改重试，先展开迭代器，确保每次都能读取同一批用户。
        tournament_users = list(tournament_users)
        if not tournament_users:
            return

        if 'score_current' in fields:
            # 同时监视时间基准和积分排行；发生并发写入时重新换算，避免混用基准。
            cache.transaction(
                lambda pipe: self._update_tournament_users_with_score_current(pipe, tournament_users, fields),
                TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY, TOURNAMENT_USER_CACHE_KEYS['score_current'],
            )
            return

        pipe = cache.pipeline()
        self._update_tournament_users_in_pipeline(pipe, tournament_users, fields)
        pipe.execute()

    def rebuild_tournament_user_cache(self, *, batch_size=1000):
        # 先确定全局基准，避免分批重建时反复推进基准、衰减已写入的成员。
        score_time = TournamentUser.objects.exclude(score_current=0).aggregate(latest=Max('last_updated'))['latest']
        self.clear_tournament_user_cache()
        if score_time is not None:
            cache.set(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY, score_time.isoformat())
        batch = []
        count = 0
        for tournament_user in TournamentUser.objects.iterator(chunk_size=batch_size):
            batch.append(tournament_user)
            count += 1
            if count % batch_size == 0:
                self.update_tournament_users(batch)
                batch = []
        self.update_tournament_users(batch)
        return count

    def _update_tournament_users_with_score_current(self, pipe, tournament_users, fields):
        key = TOURNAMENT_USER_CACHE_KEYS['score_current']
        has_scores = pipe.exists(key)
        value = pipe.get(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY)
        previous_time = datetime.fromisoformat(maybe_bytes_to_str(value)) if value is not None else None
        if previous_time is None and has_scores:
            # 缺少基准时无法解释已有分数，必须重建，不能直接混入新基准的分数。
            raise RuntimeError('Current score cache has no time reference; run rebuild_tournament_user_cache.')
        # 默认零积分不参与排行，其记录创建时间也不能推进比赛时间基准。
        score_times = [user.last_updated for user in tournament_users if user.score_current != 0]
        if previous_time is not None:
            # 保留已有基准，使历史比赛重算只能换算到该基准，不能令基准回退。
            score_times.append(previous_time)
        score_time = max(score_times, default=None)

        pipe.multi()
        if previous_time is not None and score_time > previous_time:
            # 将所有已有成员乘以同一个衰减系数，包括未参加本场比赛的用户。
            pipe.zunionstore(key, {key: tournament_score_decay_factor(previous_time, score_time)})
        if score_time is not None:
            pipe.set(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY, score_time.isoformat())
        self._update_tournament_users_in_pipeline(pipe, tournament_users, fields, score_time=score_time)

    def get_tournament_user_ranking(self, field: str, *, start=0, end=20) -> tuple[list[TournamentUser], int]:
        """读取缓存内的左闭右开排行区间。"""
        key = TOURNAMENT_USER_CACHE_KEYS[field]
        total = cache.zcard(key)
        if total == 0 or start >= end:
            return [], total

        if field in TOURNAMENT_USER_ASC_FIELDS:
            user_ids = [int(user_id) for user_id in cache.zrange(key, start, end - 1)]
        else:
            user_ids = [int(user_id) for user_id in cache.zrevrange(key, start, end - 1)]

        tournament_users_by_id: dict[int, TournamentUser] = TournamentUser.objects.in_bulk(user_ids, field_name='user_id')
        return [tournament_users_by_id[user_id] for user_id in user_ids], total

    def _normalize_tournament_user_fields(self, fields):
        if fields is None:
            return TOURNAMENT_USER_RANK_FIELDS
        return tuple(field for field in fields if field in TOURNAMENT_USER_CACHE_KEYS)

    def _update_tournament_users_in_pipeline(self, pipe, tournament_users, fields, *, score_time=None):
        # 按字段汇总，每个 zset 每批最多一条 ZADD 和一条 ZREM。
        for field in fields:
            key = TOURNAMENT_USER_CACHE_KEYS[field]
            values = {}
            removed = set()
            for tournament_user in tournament_users:
                value = getattr(tournament_user, field)
                if value == TOURNAMENT_USER_DEFAULT_VALUES[field]:
                    values.pop(tournament_user.user_id, None)
                    removed.add(tournament_user.user_id)
                    continue
                if field == 'score_current':
                    # 数据库保留用户自己的时间基准，仅缓存分数换算到统一基准。
                    value *= tournament_score_decay_factor(tournament_user.last_updated, score_time)
                removed.discard(tournament_user.user_id)
                values[tournament_user.user_id] = value
            if removed:
                pipe.zrem(key, *removed)
            if values:
                pipe.zadd(key, values)


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
