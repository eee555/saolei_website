import json
from typing import Callable

from django_redis import get_redis_connection
from redis.exceptions import WatchError

from .utils import empty_record, encode_zset_score, public_record, RANK_STATS, RANKING_NAMES, RULES, update_totals

cache = get_redis_connection('saolei_website')


class SpeedRankingCache:
    def __init__(self, ranking_name: str, *, namespace: str = 'speedranking'):
        self.prefix = f'{namespace}:{ranking_name}'
        self.detail_key = f'{self.prefix}:records'

    def rank_key(self, stat: str):
        return f'{self.prefix}:{stat}'

    @property
    def keys(self):
        return [self.detail_key, *[self.rank_key(stat) for stat in RANK_STATS]]

    def get_record(self, player_id: int):
        raw = cache.hget(self.detail_key, player_id)
        return json.loads(raw) if raw else empty_record()

    def update(self, player_id: int, transform: Callable):
        """乐观锁保护读改写，将个人数据和各 zset 一次性提交。"""
        while True:
            with cache.pipeline() as pipe:
                try:
                    pipe.watch(self.detail_key)
                    raw = pipe.hget(self.detail_key, player_id)
                    previous = json.loads(raw) if raw else empty_record()
                    record = json.loads(raw) if raw else empty_record()
                    transform(record)
                    update_totals(record)
                    if record == previous:
                        return False
                    present = any(record[f'{stat}_id'] is not None for stat in RULES)
                    pipe.multi()
                    for stat in RANK_STATS:
                        encoded = None
                        if present and record[stat] is not None:
                            encoded = encode_zset_score(stat, record[stat], record['_uploads'][stat])
                        if encoded is not None:
                            pipe.zadd(self.rank_key(stat), {str(player_id): encoded})
                        elif raw and previous[stat] is not None:
                            pipe.zrem(self.rank_key(stat), player_id)
                    if present:
                        pipe.hset(self.detail_key, player_id, json.dumps(record, allow_nan=False))
                    else:
                        pipe.hdel(self.detail_key, player_id)
                    pipe.execute()
                    return True
                except WatchError:
                    continue

    def get_range(self, stat: str, start: int, end: int):
        """只读 Redis，保证分页数据、条目数与排序来自同一个快照。"""
        while True:
            with cache.pipeline() as pipe:
                try:
                    pipe.watch(self.detail_key, self.rank_key(stat))
                    count = pipe.zcard(self.rank_key(stat))
                    members = pipe.zrange(self.rank_key(stat), start, end - 1) if end > start else []
                    player_ids = [int(member) for member in members]
                    records = pipe.hmget(self.detail_key, player_ids) if player_ids else []
                    pipe.multi()
                    pipe.execute()
                    return {'count': count, 'players': [public_record(player_id, json.loads(raw)) for player_id, raw in zip(player_ids, records) if raw]}
                except WatchError:
                    continue

    def flush(self):
        cache.delete(*self.keys)

    def publish_to(self, target):
        """将临时榜原子替换为正式榜，空的小榜也会清除旧数据。"""
        with cache.pipeline() as pipe:
            for source, destination in zip(self.keys, target.keys):
                if cache.exists(source):
                    pipe.rename(source, destination)
                else:
                    pipe.delete(destination)
            pipe.execute()


def get_player_records(player_id: int):
    """一次事务读取各榜的个人纪录及从 1 开始的排名，未入榜为 None。"""
    with cache.pipeline() as pipe:
        for ranking_name in RANKING_NAMES:
            ranking = SpeedRankingCache(ranking_name)
            pipe.hget(ranking.detail_key, player_id)
            for stat in RANK_STATS:
                pipe.zrank(ranking.rank_key(stat), player_id)
        results = iter(pipe.execute())
    records = {}
    for ranking_name in RANKING_NAMES:
        raw = next(results)
        record = public_record(player_id, json.loads(raw) if raw else empty_record())
        ranks = [next(results) for stat in RANK_STATS]
        record['ranks'] = {stat: rank + 1 if rank is not None else None for stat, rank in zip(RANK_STATS, ranks)}
        records[ranking_name] = record
    return records
