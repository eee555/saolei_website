from django.core.cache import caches

from .utils import CATALOG_CACHE_KEY, CATALOG_CACHE_SECONDS


def _cache():
    return caches['default']


def read_catalog():
    return _cache().get(CATALOG_CACHE_KEY)


def write_catalog(payload):
    _cache().set(CATALOG_CACHE_KEY, payload, CATALOG_CACHE_SECONDS)


def invalidate_catalog():
    _cache().delete(CATALOG_CACHE_KEY)
