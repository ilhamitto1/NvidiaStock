import json
from typing import Any

from app.config import settings

_memory_cache: dict[str, tuple[Any, float | None]] = {}
_redis = None
_redis_checked = False


def _get_redis():
    global _redis, _redis_checked
    if _redis_checked:
        return _redis
    _redis_checked = True
    try:
        import redis
        client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        _redis = client
    except Exception:
        _redis = None
    return _redis


def cache_get(key: str) -> Any | None:
    client = _get_redis()
    if client:
        try:
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass

    entry = _memory_cache.get(key)
    if entry:
        return entry[0]
    return None


def cache_delete(key: str) -> None:
    client = _get_redis()
    if client:
        try:
            client.delete(key)
        except Exception:
            pass
    _memory_cache.pop(key, None)


def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    client = _get_redis()
    if client:
        try:
            client.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl_seconds)
            return
        except Exception:
            pass

    _memory_cache[key] = (value, ttl)
