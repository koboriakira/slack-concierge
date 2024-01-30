from datetime import timedelta
from typing import Optional, Any
from util.datetime import now as _now

class CacheValue:
    def __init__(self, value):
        self.value = None
        self.expires_at = _now() + timedelta(minutes=5)


cache: dict[str, CacheValue] = {}

class Cache:
    @staticmethod
    def get(key) -> Optional[Any]:
        global cache
        now = _now()
        cache_item = cache.get(key)
        if cache_item is None:
            return None
        if now.timestamp() >= cache_item.expires_at.timestamp():
            return None
        return cache_item.value

    @staticmethod
    def set(key, value):
        global cache
        cache[key] = CacheValue(value)

    @classmethod
    def contains(key):
        global cache
        return key in cache
