from datetime import datetime
import json
from typing import Iterable

from django.db.models import Manager, QuerySet
from django_redis import get_redis_connection
from redis.client import Pipeline, Redis

from customranking.models import CustomPluckRecord
from videomanager.models import MAX_TIMEMS

cache = get_redis_connection('saolei_website')


class PLuckRankingCache:
    level: str
    pipe: Pipeline | None
    rank_key: str
    detail_key: str

    def __init__(self, level: str):
        self.pipe = None
        self.level = level
        self.rank_key = get_custom_pluck_rank_key(level)
        self.detail_key = get_custom_pluck_detail_key(level)

    @property
    def client(self) -> Redis | Pipeline:
        return self.pipe or cache

    def open(self):
        self.pipe = cache.pipeline()
        return self

    def close(self):
        if self.pipe is None:
            return None
        result = self.pipe.execute()
        self.pipe = None
        return result

    def __len__(self):
        return cache.zcard(self.rank_key)

    def range(self, start: int, end: int, withscores: bool = False):
        return cache.zrange(self.rank_key, start, end, withscores=withscores)

    def details(self, members: Iterable[str]):
        return cache.hmget(self.detail_key, members)

    def get_rank_range(self, start: int, end: int):
        """读取缓存内的左闭右开排行区间。"""
        members_with_scores = self.range(start, end - 1, withscores=True)
        if not members_with_scores:
            return []

        members = [
            member.decode() if isinstance(member, bytes) else member
            for member, _ in members_with_scores
        ]
        details = self.details(members)
        players = []
        for member, (_, score), detail in zip(members, members_with_scores, details):
            if detail is None:
                continue
            if isinstance(detail, bytes):
                detail = detail.decode()
            players.append(cache_to_dict(member, score, json.loads(detail)))
        return players

    def add_record(self, record: CustomPluckRecord):
        member = str(record.player_id)
        self.client.zadd(self.rank_key, {member: record_to_score(record)})
        self.client.hset(self.detail_key, member, json.dumps(record_to_detail(record)))

    def remove_record(self, player_id: int):
        member = str(player_id)
        self.client.zrem(self.rank_key, member)
        self.client.hdel(self.detail_key, member)

    def add_record_batch(self, records: Iterable[CustomPluckRecord]):
        # 准备批量数据
        rank_mapping = {}  # {member: score}
        detail_mapping = {}  # {member: detail_json}

        if isinstance(records, Manager):
            _records = list(records.all())
        elif isinstance(records, QuerySet):
            _records = list(records)
        else:
            _records = records

        for record in _records:
            member = str(record.player_id)
            rank_mapping[member] = record_to_score(record)
            detail_mapping[member] = json.dumps(record_to_detail(record))

        if rank_mapping:
            self.client.zadd(self.rank_key, rank_mapping)  # 批量ZADD
            self.client.hset(self.detail_key, mapping=detail_mapping)  # 批量HSET (某些客户端库支持)

    def flush(self):
        self.client.delete(
            self.rank_key,
            self.detail_key,
            get_legacy_custom_pluck_player_key(self.level),
        )


##############
# Cache Keys #
##############

def get_custom_pluck_rank_key(level: str) -> str:
    """
    有序集zset，排序键`score`通常是`pluck`；当`pluck == 0`时使用`timems - MAX_TIMEMS`降低 0 碰撞风险。`member`是`player_id`。
    """
    return f'customranking:pluck:{level}:rank'


def get_custom_pluck_detail_key(level: str) -> str:
    """
    查找表hset，主键是RANK的`member`，存储 API 展示需要的录像信息。
    """
    return f'customranking:pluck:{level}:detail'


def get_legacy_custom_pluck_player_key(level: str) -> str:
    """旧缓存结构中的玩家索引，flush时顺便清理。"""
    return f'customranking:pluck:{level}:player'


###################
# Data Conversion #
###################

def record_to_score(record: CustomPluckRecord):
    """将数据库纪录转换为 Redis zset score。"""
    if record.pluck > 0:
        return record.pluck
    return record.timems - MAX_TIMEMS


def record_to_detail(record: CustomPluckRecord):
    """将数据库纪录转换为 Redis detail hash 中保存的展示信息。"""
    return {
        'video_id': record.video_id,
        'mode': record.video.mode,
        'timems': record.timems,
        'bv': record.video.bv,
        'upload_time': record.upload_time.isoformat(),
    }


def cache_to_dict(member: str, score: float, detail: dict):
    """将 Redis 排行缓存中的数据转换为字典。"""
    data = {**detail}
    upload_time = data.pop('upload_time')
    return {
        **data,
        'player_id': int(member),
        'pluck': max(0, score),
        'upload_time': datetime.fromisoformat(upload_time),
    }


def get_player_pluck_records(player_id: int, levels: Iterable[str]):
    """用 Redis pipeline 批量读取玩家在多个配置下的当前纪录。"""
    ranking_caches = [
        PLuckRankingCache(level)
        for level in levels
    ]
    if not ranking_caches:
        return {}

    member = str(player_id)
    pipe = cache.pipeline()
    for ranking_cache in ranking_caches:
        pipe.zscore(ranking_cache.rank_key, member)
        pipe.hget(ranking_cache.detail_key, member)

    results = pipe.execute()
    records_by_level = {}
    for index, ranking_cache in enumerate(ranking_caches):
        score = results[index * 2]
        detail = results[index * 2 + 1]
        if score is None or detail is None:
            continue
        if isinstance(detail, bytes):
            detail = detail.decode()
        records_by_level[ranking_cache.level] = cache_to_dict(
            member,
            score,
            json.loads(detail),
        )
    return records_by_level
