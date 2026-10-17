from typing import Literal

TopLevel = Literal['b', 'i', 'e']
TopStat = Literal['t', 'b', 's']
MINIMUM_BV = {'b': 10, 'i': 30, 'e': 100}
STAT_COLUMNS = {'t': 'timems', 'b': 'bvs', 's': 'iqg'}
TOP_SIZE = 5
ANCHOR_SIZE = 20
MISSING_TIMEMS = 999999


def record_field(nf: bool, level: str, stat: str) -> str:
    return f'{"nf" if nf else "std"}:{level}{stat}'


RANK_FIELDS = tuple(record_field(nf, level, stat) for nf in (False, True) for level in MINIMUM_BV for stat in STAT_COLUMNS)


def parse_field(field: str):
    mode, code = field.split(':')
    return mode == 'nf', code[0], code[1]


def score(stat: str, value: float) -> float:
    return value if stat == 't' else -value


def stat_record(stat: str, videos: list[dict]) -> dict:
    """由真实前五计算均值，缺项仅补成绩，不伪造录像。"""
    missing = (TOP_SIZE - len(videos)) * MISSING_TIMEMS if stat == 't' else 0
    return {'mean': (sum(video['value'] for video in videos) + missing) / TOP_SIZE, 'videos': videos}


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
