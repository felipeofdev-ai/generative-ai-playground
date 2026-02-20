"""Redis cache client."""

import json
import time
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def check_redis_health() -> bool:
    try:
        await get_redis().ping()
        return True
    except Exception:
        return False


async def cache_get(key: str) -> Any | None:
    data = await get_redis().get(key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    await get_redis().setex(key, ttl, json.dumps(value, default=str))


async def cache_delete(key: str) -> None:
    await get_redis().delete(key)


async def rate_limit_check(key: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
    """Sliding window rate limit. Returns (allowed, remaining)."""
    lua = """
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window * 1000)
    local count = redis.call('ZCARD', key)
    if count < limit then
        redis.call('ZADD', key, now, now)
        redis.call('EXPIRE', key, window)
        return {1, limit - count - 1}
    end
    return {0, 0}
    """
    now = int(time.time() * 1000)
    result = await get_redis().eval(lua, 1, key, limit, window_seconds, now)
    return bool(result[0]), int(result[1])
