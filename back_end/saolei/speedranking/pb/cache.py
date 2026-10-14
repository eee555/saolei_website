import json

from .utils import member, parse_field, parse_member, record_field, record_from_score, upload_time_from_score
from ..cache import cache, pipeline


class PBRankingCache:
    def __init__(self, namespace: str = 'speedranking:pb'):
        self.prefix = namespace

    def rank_key(self, field: str):
        return f'{self.prefix}:{field}'

    def player_key(self, player_id: int):
        return f'{self.prefix}:player:{player_id}'

    @property
    def counts_key(self):
        return f'{self.prefix}:counts'

    def get_counts(self):
        """一次读取各小榜人数，未出现的 field 视为 0。"""
        return {(field.decode() if isinstance(field, bytes) else field): int(count) for field, count in cache.hgetall(self.counts_key).items()}

    def read_records(self, pipe, player_ids):
        for player_id in player_ids:
            pipe.hgetall(self.player_key(player_id))

    def unpack_records(self, results, player_ids):
        return {
            player_id: {(field.decode() if isinstance(field, bytes) else field): json.loads(raw) for field, raw in rows.items()}
            for player_id, rows in zip(player_ids, results)
        }

    def get_player_records(self, player_id: int):
        rows = cache.hgetall(self.player_key(player_id))
        records = self.unpack_records([rows], [player_id])[player_id]
        result = []
        for field, record in sorted(records.items()):
            nf, level, bv = parse_field(field)
            result.append({'nf': nf, 'level': level, 'bv': bv, **record})
        return result

    def get_range(self, nf: bool, level: str, bv: int, start: int, end: int):
        key = self.rank_key(record_field(nf, level, bv))
        with pipeline() as pipe:
            pipe.zcard(key)
            if end > start:
                pipe.zrange(key, start, end - 1, withscores=True)
            results = pipe.execute()
        rows = results[1] if end > start else []
        players = []
        for value, score in rows:
            player_id, video_id = parse_member(value)
            players.append({'player_id': player_id, 'upload_time': upload_time_from_score(score), **record_from_score(video_id, score)})
        return {'count': results[0], 'players': players}

    def read_scores(self, previous, keys):
        """rank hash 提供旧录像 id，只需查询这些已知 member 的 score。"""
        scores = dict.fromkeys(keys)
        present = [key for key in keys if previous[key[0]].get(key[1])]
        with pipeline() as pipe:
            for player_id, field in present:
                old = previous[player_id][field]
                pipe.zscore(self.rank_key(field), member(player_id, old['video_id']))
            results = pipe.execute()
        scores.update(zip(present, results))
        return scores

    def write_changes(self, pipe, previous, changes):
        for (player_id, field), candidate in changes.items():
            old = previous[player_id].get(field)
            if old:
                pipe.zrem(self.rank_key(field), member(player_id, old['video_id']))
            if candidate is None:
                pipe.hdel(self.player_key(player_id), field)
            else:
                video_id, score = candidate
                pipe.zadd(self.rank_key(field), {member(player_id, video_id): score})
                pipe.hset(self.player_key(player_id), field, json.dumps(record_from_score(video_id, score)))

    def read_ranks(self, members):
        """批量读取本次变化的 member 排名，不查询其他用户。"""
        members = list(members)
        with pipeline() as pipe:
            for field, value in members:
                pipe.zrank(self.rank_key(field), value)
            results = pipe.execute()
        ranks = {}
        for (field, _), rank in zip(members, results):
            if rank is not None:
                ranks.setdefault(field, []).append(rank)
        return ranks

    def read_previous_ranks(self, previous, changes):
        members = []
        for player_id, field in changes:
            old = previous[player_id].get(field)
            if old:
                members.append((field, member(player_id, old['video_id'])))
        return self.read_ranks(members)

    def refresh_changed_ranks(self, previous_ranks, changes):
        """替换刷新旧、新排名之间；人数改变则从最早受影响排名刷新至榜尾。"""
        new_ranks = self.read_ranks((field, member(player_id, candidate[0])) for (player_id, field), candidate in changes.items() if candidate is not None)
        ranges = {}
        for field in {ranking_field for _, ranking_field in changes}:
            old = previous_ranks.get(field, [])
            new = new_ranks.get(field, [])
            positions = old + new
            if not positions:
                ranges[field] = 0, -1
                continue
            end = max(positions) if len(old) == len(new) else -1
            ranges[field] = min(positions), end
        self.refresh_ranks(ranges)

    def refresh_ranks(self, ranges):
        """批量刷新指定排名区间及小榜人数，区间使用从 0 开始的闭区间。"""
        ranges = list(ranges.items())
        with pipeline() as pipe:
            for field, (start, end) in ranges:
                pipe.zrange(self.rank_key(field), start, end, withscores=True)
                pipe.zcard(self.rank_key(field))
            results = pipe.execute()
        with pipeline() as pipe:
            for (field, (start, _)), rows, count in zip(ranges, results[::2], results[1::2]):
                pipe.hset(self.counts_key, field, count)
                for rank, (value, score) in enumerate(rows, start=start + 1):
                    player_id, video_id = parse_member(value)
                    pipe.hset(self.player_key(player_id), field, json.dumps(record_from_score(video_id, score, rank)))
            pipe.execute()

    def remove_player_members(self, pipe, player_id: int, field: str):
        """管理员修复时清除竞争可能留下的多余 member，不依赖旧 hash 的正确性。"""
        members = [(field, value) for value, _ in cache.zscan_iter(self.rank_key(field), match=f'{player_id}:*')]
        previous_ranks = self.read_ranks(members)
        for _, value in members:
            pipe.zrem(self.rank_key(field), value)
        pipe.hdel(self.player_key(player_id), field)
        return previous_ranks

    def ranking_fields(self):
        for mode in ('std', 'nf'):
            for key in cache.scan_iter(match=f'{self.prefix}:{mode}:*'):
                key = key.decode() if isinstance(key, bytes) else key
                yield key[len(self.prefix) + 1:]

    def flush(self):
        keys = []
        for key in cache.scan_iter(match=f'{self.prefix}:*'):
            keys.append(key)
            if len(keys) >= 1000:
                cache.delete(*keys)
                keys.clear()
        if keys:
            cache.delete(*keys)
