import redis.asyncio as redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_TTL = 1800  # 30 minutes in seconds

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

async def get_history(session_id: str) -> list:
    """Fetch conversation history for a session."""
    data = await r.get(f"session:{session_id}")
    if data:
        return json.loads(data)
    return []

async def save_history(session_id: str, history: list):
    """Save updated history and reset the 30-min expiry."""
    await r.setex(
        f"session:{session_id}",
        SESSION_TTL,
        json.dumps(history)
    )

async def clear_session(session_id: str):
    """Manually clear a session."""
    await r.delete(f"session:{session_id}")