import asyncio
from typing import Optional

from request_coalescing_py.models import Item
from request_coalescing_py.database import DatabaseRepo


class CoalescingRepo:
    """The coalescing repository.

    This repository is responsible for creating, queuing and
    processing futures (for requests).

    Attributes:
        _repo (DatabaseRepo): Downstream repository called to perform actual requests
        _queue (asyncio.Queue): A task queue of requested item_ids awaiting asyncio.Future results
        _queued (dict): A map of item_ids (int) -> pending futures (asyncio.Future)

    """

    def __init__(self, repo: DatabaseRepo):
        """Initialise the coalescing repository.

        Args:
            repo (DatabaseRepo): The downstream database repository to be used 
                when performing actual requests

        """
        self._repo = repo

        self._queue = asyncio.Queue()
        self._queued = {}

    async def get_by_id(self, item_id: int) -> "asyncio.Future[Optional[Item]]":
        """Get an item by a specified id.

        If there isn't already a pending future, for a requested item_id,
        then a new future will be created and added to the task queue,
        otherwise the existing future will be returned.

        Args:
            item_id (int): The requested item's id.

        Returns:
            asyncio.Future[Optional[Item]]: A future pending result.

        """
        # Check if there is an already pending task for that item.
        fut = self._queued.get(item_id)
        if fut:
            return fut
        
        # There is not a pending task.
        # Create a new future and add to the task queue.
        fut = asyncio.get_event_loop().create_future()
        self._queued[item_id] = fut
        await self._queue.put(item_id)
        return fut

    async def process_queue(self) -> None:
        """This subroutine is responsible for processing the
        requests in the task queue.

        1) Recieves an item_id from the task queue
        2) Performs the request for the item (by calling the downstream
            database `_repo`)
        3) Sets the result of the future (fulfilling all pending requests
            for that item)
        4) Marks the task as complete.

        """
        while True:
            item_id = await self._queue.get()
            item = await self._repo.get_by_id(item_id)
            self._queued[item_id].set_result(item)
            del self._queued[item_id]
            self._queue.task_done()
