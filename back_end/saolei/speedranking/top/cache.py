import json

from .utils import ANCHOR_SIZE, parse_field, RANK_FIELDS, score
from ..cache import cache, pipeline


class TopRankingCache:
    def __init__(self, namespace: str = 'speedranking'):
        self.prefix = f'{namespace}:top'
        self.detail_key = f'{self.prefix}:records'
        self.anchors_key = f'{self.prefix}:anchors'

    def rank_key(self, field: str) -> str:
        return f'{self.prefix}:{field}'

    @property
    def keys(self):
        return [self.detail_key, self.anchors_key, *[self.rank_key(field) for field in RANK_FIELDS]]

    def read_records(self, pipe, player_ids):
        """将用户明细批量读取加入共享 pipeline。"""
        pipe.hmget(self.detail_key, player_ids)

    @staticmethod
    def unpack_records(rows, player_ids):
        return {player_id: json.loads(raw) if raw else {} for player_id, raw in zip(player_ids, rows)}

    def get_record(self, player_id: int):
        raw = cache.hget(self.detail_key, player_id)
        return json.loads(raw) if raw else {}

    def write_record(self, pipe, player_id: int, record: dict):
        """保存用户原始均值与前五明细，空纪录删除。"""
        if record:
            pipe.hset(self.detail_key, player_id, json.dumps(record, allow_nan=False))
        else:
            pipe.hdel(self.detail_key, player_id)

    def write_score(self, pipe, player_id: int, field: str, value: float | None):
        if value is None:
            pipe.zrem(self.rank_key(field), player_id)
        else:
            pipe.zadd(self.rank_key(field), {str(player_id): value})

    def get_range(self, field: str, start: int, end: int):
        """按小榜索引取用户，返回该页各用户的完整 hash 纪录，不回源。"""
        with pipeline() as pipe:
            pipe.zcard(self.rank_key(field))
            if end > start:
                pipe.zrange(self.rank_key(field), start, end - 1)
            results = pipe.execute()
        player_ids = [int(member) for member in results[1]] if end > start else []
        rows = cache.hmget(self.detail_key, player_ids) if player_ids else []
        players = []
        for player_id, raw in zip(player_ids, rows):
            if raw is not None:
                players.append({'player_id': player_id, 'records': json.loads(raw)})
        return {'count': results[0], 'players': players}

    def refresh_anchors(self, fields: set[str]):
        """每个变动小榜最多读取二十个 score，批量更新锚点。"""
        if not fields:
            return
        fields = sorted(fields)
        with pipeline() as pipe:
            for field in fields:
                pipe.zrange(self.rank_key(field), 0, ANCHOR_SIZE - 1, withscores=True)
            rows = pipe.execute()
        anchors = {}
        for field, entries in zip(fields, rows):
            stat = parse_field(field)[2]
            value = sum(score(stat, value) for member, value in entries) / len(entries) if entries else 0
            anchors[field] = json.dumps({'value': value, 'sample_count': len(entries)}, allow_nan=False)
        cache.hset(self.anchors_key, mapping=anchors)

    def get_anchors(self):
        """一次读取完整锚点 hash，不筛选字段或补齐缺项。"""
        return {field.decode() if isinstance(field, bytes) else field: json.loads(raw) for field, raw in cache.hgetall(self.anchors_key).items()}

    def flush(self):
        cache.delete(*self.keys)

    def publish_to(self, target):
        """将临时明细、十八个索引及锚点一并原子发布。"""
        with pipeline() as pipe:
            for source, destination in zip(self.keys, target.keys):
                if cache.exists(source):
                    pipe.rename(source, destination)
                else:
                    pipe.delete(destination)
            pipe.execute()
