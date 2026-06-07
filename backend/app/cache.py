import hashlib
import json
from typing import Any, Optional
import redis.asyncio as aioredis


async def get_cache_key(prefix: str, user_id: int, data: str) -> str:
    """Generate a deterministic cache key."""
    digest = hashlib.sha256(f"{user_id}:{data}".encode()).hexdigest()[:16]
    return f"{prefix}:{user_id}:{digest}"


async def get_cached(redis_client: aioredis.Redis, key: str) -> Optional[Any]:
    """Retrieve cached value."""
    if not redis_client:
        return None
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None


async def set_cached(redis_client: aioredis.Redis, key: str, value: Any, ttl: int = 3600) -> None:
    """Store value in cache with TTL (default 1 hour)."""
    if not redis_client:
        return
    await redis_client.set(key, json.dumps(value), ex=ttl)


async def delete_cached(redis_client: aioredis.Redis, key: str) -> None:
    """Delete a cached key."""
    if not redis_client:
        return
    await redis_client.delete(key)


async def invalidate_user_cache(redis_client: aioredis.Redis, user_id: int, prefix: str) -> None:
    """Invalidate all cache keys for a user with given prefix."""
    if not redis_client:
        return
    pattern = f"{prefix}:{user_id}:*"
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
