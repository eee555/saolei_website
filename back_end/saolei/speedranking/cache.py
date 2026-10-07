from django_redis import get_redis_connection

cache = get_redis_connection('saolei_website')


def pipeline():
    return cache.pipeline()
