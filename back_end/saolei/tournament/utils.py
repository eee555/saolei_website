from datetime import timedelta
import secrets
import string
from typing import Any

MAX_TOURNAMENT_BEST = 9223372036854775807
TOURNAMENT_SCORE_HALF_LIFE = timedelta(days=365 * 2)


def generate_random_token(length=5):
    """生成指定位数的随机字母数字混合码"""
    alphabet = string.ascii_letters + string.digits  # 大小写字母+数字
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def insert_to_id_value_list_asc(list_asc: list[tuple[int, Any]], video_id: int, value: Any):
    insert_index = len(list_asc)
    for i, item in enumerate(list_asc):
        if value < item[1]:
            insert_index = i
            break
    list_asc.insert(insert_index, (video_id, value))
    list_asc.pop()


def default_weekly_classic_et():
    return [(0, 240000), (0, 240000)]


def default_weekly_classic_it():
    return [(0, 60000), (0, 60000), (0, 60000), (0, 60000), (0, 60000)]


def tournament_score_decay_factor(start_time, end_time):
    if end_time <= start_time:
        return 1
    elapsed_seconds = (end_time - start_time).total_seconds()
    half_life_seconds = TOURNAMENT_SCORE_HALF_LIFE.total_seconds()
    return 1 / (2 ** (elapsed_seconds / half_life_seconds))
