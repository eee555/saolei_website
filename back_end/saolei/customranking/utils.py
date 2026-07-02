from .config import CUSTOM_PLUCK_CACHE_SIZE


def get_custom_pluck_cache_key(level: str) -> str:
    return f'customranking:pluck:{level}:top{CUSTOM_PLUCK_CACHE_SIZE}'
