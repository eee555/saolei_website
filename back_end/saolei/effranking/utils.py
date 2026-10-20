from contextlib import contextmanager
import logging

logger = logging.getLogger('effranking')


@contextmanager
def log_update_errors(operation: str, **context):
    """记录更新异常及已有上下文，保持原有异常传播。"""
    try:
        yield
    except Exception:
        logger.exception('Efficiency ranking update failed: %s %s', operation, context)
        raise
