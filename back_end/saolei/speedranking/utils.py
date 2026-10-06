from contextlib import contextmanager
from datetime import datetime, timezone
import logging

logger = logging.getLogger('speedranking')


@contextmanager
def log_update_errors(operation: str, **context):
    """更新失败时记录上下文及堆栈，并保持异常传播。"""
    try:
        yield
    except Exception:
        logger.exception('Ranking update failed: %s %s', operation, context)
        raise


def upload_microseconds(upload_time: datetime) -> int:
    delta = upload_time - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds


def player_batches(videos, batch_size: int):
    last_player = 0
    while players := list(videos.filter(player_id__gt=last_player).order_by('player_id').values_list('player_id', flat=True).distinct()[:batch_size]):
        yield players
        last_player = players[-1]
