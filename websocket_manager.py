
from typing import Dict, Set
from fastapi import WebSocket
import asyncio

job_subscribers: Dict[str, Set[WebSocket]] = {}
subscribers_lock = asyncio.Lock()

async def broadcast(payload: dict):
    job_id = payload.get("job_id")
    async with subscribers_lock:
        conns = list(job_subscribers.get(job_id, set()))
    for ws in conns:
        try: await ws.send_json(payload)
        except: pass
