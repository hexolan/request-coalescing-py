import asyncio
from typing import Optional

from fastapi import FastAPI
from databases import Database

from request_coalescing_py.models import Item


class DatabaseRepo:
    """The database repository.

    This repository is responsible for database operations.

    Attributes:
        app (FastAPI): The application instance (for access to the metrics object in state).
        _db (databases.Database): The database instance used for requests.

    """

    def __init__(self, app: FastAPI) -> None:
        """Initialise the database repository.

        Args:
            app (FastAPI): The application instance.

        """
        self.app = app

    async def start_db(self) -> None:
        """Opens a database connection and prepare the environment."""
        self._db = Database("sqlite://./test.db")
        await self._db.connect()
        
        try:
            await self._db.execute(query="CREATE TABLE IF NOT EXISTS 'items' (id INTEGER PRIMARY KEY, name TEXT)")
            await self._db.execute(query="INSERT INTO 'items' (id, name) VALUES (1, 'Test Item')")
        except Exception:
            pass

    async def stop_db(self) -> None:
        """Gracefully closes the database connection."""
        await self._db.disconnect()

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get an item by a specified id (from the database).

        Args:
            item_id (int): The requested item's id.

        Returns:
            Optional[Item]: The item details (if found) or None.

        """
        self.app.state.metrics["db_calls"] += 1

        # Simulate expensive read (50ms)
        await asyncio.sleep(.05)

        row = await self._db.fetch_one(query="SELECT * FROM 'items' WHERE id = :id", values={"id": item_id})
        if row:
            return Item(**row._mapping)
        
        return None
