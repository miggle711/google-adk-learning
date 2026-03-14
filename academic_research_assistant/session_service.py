import os
import json
import time
from typing import Optional

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None


class RedisSessionService:
    """A minimal Redis-backed session service

    Methods implemented mirror the small subset used by the codebase:
    - async create_session(app_name, user_id, session_id)
    - async get_session(session_id)
    - async delete_session(session_id)
    - async close()

    If `redis` is not available at runtime, initialization will raise an ImportError.
    """

    def __init__(self, redis_url: Optional[str] = None, prefix: str = "ara:session:"):
        if aioredis is None:
            raise ImportError("redis.asyncio is required for RedisSessionService")

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.prefix = prefix
        # decode_responses True to work with text directly
        self._client = aioredis.from_url(self.redis_url, decode_responses=True)

    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    async def create_session(self, app_name: str, user_id: str, session_id: str, data: Optional[dict] = None):
        key = self._key(session_id)
        payload = {
            "app_name": app_name,
            "user_id": user_id,
            "created_at": str(int(time.time())),
        }
        if data is not None:
            payload["data"] = json.dumps(data)

        await self._client.hset(key, mapping=payload)
        return True

    async def get_session(self, session_id: str):
        key = self._key(session_id)
        result = await self._client.hgetall(key)
        if not result:
            return None
        if "data" in result:
            try:
                result["data"] = json.loads(result["data"])
            except Exception:
                pass
        return result

    async def delete_session(self, session_id: str):
        key = self._key(session_id)
        return await self._client.delete(key)

    async def close(self):
        try:
            await self._client.close()
            await self._client.connection_pool.disconnect()
        except Exception:
            pass


def get_session_service():
    """Factory that returns a RedisSessionService when `REDIS_URL` is configured.

    Falls back to `google.adk.sessions.InMemorySessionService` if Redis is not configured
    or cannot be imported. This keeps behavior backwards compatible for local/dev runs.
    """
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return RedisSessionService(redis_url)

    try:
        # Prefer the ADK-provided in-memory service when Redis isn't configured
        from google.adk.sessions import InMemorySessionService

        return InMemorySessionService()
    except Exception:
        # Last-resort: create a local RedisSessionService pointing to default URL.
        # This will raise ImportError if the redis package is missing.
        return RedisSessionService()
