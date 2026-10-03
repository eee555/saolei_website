from django_redis import get_redis_connection


def get_local_snapshot_cache():
    """拒绝向非本地 Redis 导入测试快照。"""
    cache = get_redis_connection('saolei_website')
    host = cache.connection_pool.connection_kwargs.get('host')
    if host not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Snapshot import requires a loopback Redis connection')
    cache.ping()
    return cache


def reset_local_snapshot_cache():
    get_local_snapshot_cache().flushdb()
