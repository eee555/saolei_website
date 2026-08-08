import secrets
import string
from typing import Any


def generate_random_token(length=5):
    """生成指定位数的随机字母数字混合码"""
    alphabet = string.ascii_letters + string.digits  # 大小写字母+数字
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def insert_to_id_value_list_asc(list_asc: list[tuple[int, Any]], video_id: int, value: Any):
    for i in range(len(list_asc) - 1, -1, -1):
        if list_asc[i][1] < value:
            break
    list_asc.insert(i, (video_id, value))
    list_asc.pop()
