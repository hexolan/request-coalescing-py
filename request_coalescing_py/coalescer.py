import asyncio
from typing import Optional

from request_coalescing_py.models import Item
from request_coalescing_py.database import DatabaseRepo


class CoalescingRepo:
    def __init__(self, repo: DatabaseRepo):
        self._repo = repo

        self._queue = asyncio.Queue()
        self._queued = {}  # map of item_id: future

    async def get_by_id(self, item_id: int) -> "asyncio.Future[Optional[Item]]":
        # Check if there is an already pending request for that item.
        fut = self._queued.get(item_id)
        if fut:
            return fut
        
        # There is not a pending request.
        fut = asyncio.get_event_loop().create_future()
        self._queued[item_id] = fut
        await self._queue.put(item_id)
        return fut

    async def process_queue(self) -> None:
        while True:
            item_id = await self._queue.get()
            item = await self._repo.get_by_id(item_id)
            self._queued[item_id].set_result(item)
            del self._queued[item_id]
            self._queue.task_done()
