import math

from .config import CUSTOM_PLUCK_CACHE_SIZE


def normalize_pluck(value) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        return None
    return value


def get_custom_pluck_cache_key(level: str) -> str:
    return f'customranking:pluck:{level}:top{CUSTOM_PLUCK_CACHE_SIZE}'
