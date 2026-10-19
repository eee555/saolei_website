from typing import Literal

TopLevel = Literal['b', 'i', 'e']
TopStat = Literal['t', 'b', 's']
MINIMUM_BV = {'b': 10, 'i': 30, 'e': 100}
STAT_COLUMNS = {'t': 'timems', 'b': 'bvs', 's': 'iqg'}
TOP_SIZE = 5
ANCHOR_SIZE = 20
MISSING_TIMEMS = 999999
SOFT_WEIGHTS = {'b': {'t': 28, 'b': 48, 's': 24}, 'i': {'t': 34, 'b': 34, 's': 32}, 'e': {'t': 33, 'b': 33, 's': 34}}
LEVEL_WEIGHTS = {'b': 6, 'i': 14, 'e': 20}
SOFT_FIELDS = tuple(f'{mode}:{level}' for mode in ('std', 'nf') for level in (*MINIMUM_BV, 'sum')) + ('lsf',)


def record_field(nf: bool, level: str, stat: str) -> str:
    return f'{"nf" if nf else "std"}:{level}{stat}'


RANK_FIELDS = tuple(record_field(nf, level, stat) for nf in (False, True) for level in MINIMUM_BV for stat in STAT_COLUMNS)


def parse_field(field: str):
    mode, code = field.split(':')
    return mode == 'nf', code[0], code[1]


def score(stat: str, value: float) -> float:
    return value if stat == 't' else -value


def stat_record(stat: str, videos: list[dict]) -> dict:
    """仅保存真实前五，均值按需计算。"""
    return {'videos': videos}


def record_mean(stat: str, record: dict | None) -> float:
    """真实成绩补齐五项后计算均值，不写入缓存明细。"""
    videos = record['videos'] if record else []
    missing = (TOP_SIZE - len(videos)) * MISSING_TIMEMS if stat == 't' else 0
    return (sum(video['value'] for video in videos) + missing) / TOP_SIZE


def ranking_score(stat: str, value: float) -> float:
    """排序索引统一使用越大越好的变换值。"""
    if stat == 't':
        return 1 / (value if value > 0 else MISSING_TIMEMS)
    return value ** (1 / 1.7) if stat == 's' else value


def original_value(stat: str, value: float) -> float:
    """逆变换 score，供原始锚点求算术平均。"""
    if stat == 't':
        return 1 / value if value > 0 else MISSING_TIMEMS
    return value ** 1.7 if stat == 's' else value


def soft_coefficients(anchors: dict, mode: str, level: str) -> dict[str, float]:
    """将锚点与指标权重转换为线性组合系数。"""
    coefficients = {}
    for stat, weight in SOFT_WEIGHTS[level].items():
        anchor = anchors.get(f'{mode}:{level}{stat}', {}).get('value', 0)
        coefficients[stat] = weight / ranking_score(stat, anchor) if anchor > 0 else 0
    return coefficients


def soft_values(records: dict, anchors: dict) -> dict[str, float]:
    """按同一锚点快照计算用户全部九项软实力。"""
    values = {}
    for mode in ('std', 'nf'):
        for level in MINIMUM_BV:
            coefficients = soft_coefficients(anchors, mode, level)
            values[f'{mode}:{level}'] = sum(
                coefficients[stat] * ranking_score(stat, record_mean(stat, records.get(f'{mode}:{level}{stat}')))
                for stat in STAT_COLUMNS
            )
        values[f'{mode}:sum'] = sum(values[f'{mode}:{level}'] * weight for level, weight in LEVEL_WEIGHTS.items())
    values['lsf'] = values['std:sum'] * 0.97 + values['nf:sum'] * 0.03
    return values


def insert_video(stat: str, videos: list[dict], candidate: dict) -> list[dict]:
    """维护至多五条有序成绩，同分不替换末项。"""
    videos = [video for video in videos if video['video_id'] != candidate['video_id']]
    value = score(stat, candidate['value'])
    if len(videos) == TOP_SIZE and value >= score(stat, videos[-1]['value']):
        return videos
    index = next((index for index, video in enumerate(videos) if value < score(stat, video['value'])), len(videos))
    return (videos[:index] + [candidate] + videos[index:])[:TOP_SIZE]


def merge_videos(stat: str, previous: list[dict], candidates: list[dict]) -> list[dict]:
    """批量候选按录像 id 去重后与现有前五合并。"""
    videos = {video['video_id']: video for video in previous}
    videos.update((video['video_id'], video) for video in candidates)
    return sorted(videos.values(), key=lambda video: score(stat, video['value']))[:TOP_SIZE]
