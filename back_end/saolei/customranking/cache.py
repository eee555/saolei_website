from datetime import datetime, timezone
import json
from typing import Iterable

from django.db.models import Manager, QuerySet
from django_redis import get_redis_connection
from redis.client import Pipeline, Redis

from customranking.models import CustomPluckRecord

cache = get_redis_connection('saolei_website')

CUSTOM_PLUCK_CACHE_SIZE = 100


class PLuckRankingCache:
    pipe: Pipeline | None
    rank_key: str
    detail_key: str
    player_key: str

    def __init__(self, level: str):
        self.pipe = None
        self.rank_key = get_custom_pluck_rank_key(level)
        self.detail_key = get_custom_pluck_detail_key(level)
        self.player_key = get_custom_pluck_player_key(level)

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

    def get_member(self, player_id: int):
        """从玩家索引缓存中读取玩家当前对应的 zset member。"""
        member = cache.hget(self.player_key, player_id)
        if isinstance(member, bytes):
            return member.decode()
        return member

    def tail_score_and_member(self):
        """读取缓存尾端纪录的排序键。"""
        rows = self.range(-1, -1, withscores=True)
        if not rows:
            return None
        member, score = rows[0]
        if isinstance(member, bytes):
            member = member.decode()
        return score, member

    def can_insert_record(self, record: CustomPluckRecord):
        """判断纪录是否有机会进入当前缓存窗口。"""
        tail = self.tail_score_and_member()
        if tail is None:
            return False
        return (record.pluck, record_to_member(record)) <= tail

    def add_record(self, record: CustomPluckRecord):
        member = record_to_member(record)
        self.client.zadd(self.rank_key, {member: record.pluck})
        self.client.hset(self.detail_key, member, json.dumps(record_to_detail(record)))
        self.client.hset(self.player_key, record.player_id, member)

    def remove_record(self, member: str | None, player_id: int):
        if member is not None:
            self.client.zrem(self.rank_key, member)
            self.client.hdel(self.detail_key, member)
        self.client.hdel(self.player_key, player_id)

    def update_record(self, record: CustomPluckRecord, player_id: int):
        """更新 Redis 排行缓存中某个玩家的纪录。"""
        member = self.get_member(player_id)
        if member is not None:
            self.remove_record(member, player_id)
        self.add_record(record)

    def delete_record(self, player_id: int):
        """删除 Redis 排行缓存中某个玩家的纪录。"""
        member = self.get_member(player_id)
        self.remove_record(member, player_id)

    def add_record_batch(self, records: Iterable[CustomPluckRecord]):
        # 准备批量数据
        rank_mapping = {}  # {member: score}
        detail_mapping = {}  # {member: detail_json}
        player_mapping = {}  # {player_id: member} 用于 player_key

        if isinstance(records, Manager):
            _records = list(records.all())
        elif isinstance(records, QuerySet):
            _records = list(records)
        else:
            _records = records

        for record in _records:
            member = record_to_member(record)
            rank_mapping[member] = record.pluck
            detail_mapping[member] = json.dumps(record_to_detail(record))
            player_mapping[record.player_id] = member

        if rank_mapping:
            self.client.zadd(self.rank_key, rank_mapping)  # 批量ZADD
            self.client.hset(self.detail_key, mapping=detail_mapping)  # 批量HSET (某些客户端库支持)
            self.client.hset(self.player_key, mapping=player_mapping)

    def flush(self):
        self.client.delete(self.rank_key, self.detail_key, self.player_key)

    def clamp(self, target: int):
        """将排行缓存截断到指定数量，不负责补齐。"""
        target = max(target, 0)
        if len(self) <= target:
            return

        members = cache.zrange(self.rank_key, target, -1)
        members = [
            member.decode() if isinstance(member, bytes) else member
            for member in members
        ]
        player_ids = [
            member_to_player_id(member)
            for member in members
        ]

        self.client.zremrangebyrank(self.rank_key, target, -1)
        self.client.hdel(self.detail_key, *members)
        self.client.hdel(self.player_key, *player_ids)


##############
# Cache Keys #
##############

def get_custom_pluck_rank_key(level: str) -> str:
    """
    有序集zset，排序键`score`是`pluck`。同`pluck`时，再比较`time`，同`time`时比较`upload_time`。为了解决后面两个比较，`timems`和`upload_time`分别以8位整数和13位整数连接起来作为zset的主键`member`。为了彻底解决主键冲突，`member`的结尾还加上了`player_id`。
    """
    return f'customranking:pluck:{level}:rank'


def get_custom_pluck_detail_key(level: str) -> str:
    """
    查找表hset，主键是RANK的`member`，字段是`video_id`、`mode`、`bv`。其中`mode`和`bv`来自入榜录像。
    """
    return f'customranking:pluck:{level}:detail'


def get_custom_pluck_player_key(level: str) -> str:
    """
    hset，存储`player_id`到`member`的映射。
    """
    return f'customranking:pluck:{level}:player'


###################
# Data Conversion #
###################

def record_to_member(record: CustomPluckRecord) -> str:
    upload_time_ms = int(record.upload_time.timestamp() * 1000)
    return f'{record.timems:08d}:{upload_time_ms:013d}:{record.player_id}'


def member_to_player_id(member: str) -> int:
    return int(member.rsplit(':', 1)[1])


def record_to_detail(record: CustomPluckRecord):
    """将数据库纪录转换为 Redis detail hash 中保存的展示信息。"""
    return {
        'video_id': record.video_id,
        'mode': record.video.mode,
        'bv': record.video.bv,
    }


def cache_to_dict(member: str, score: float, detail: dict):
    """将 Redis 排行缓存中的数据转换为字典。"""
    timems, upload_time_ms, player_id = member.split(':', 2)
    return {
        **detail,
        'player_id': int(player_id),
        'pluck': score,
        'timems': int(timems),
        'upload_time': datetime.fromtimestamp(int(upload_time_ms) / 1000, tz=timezone.utc),
    }


