import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from request_coalescing_py.main import app
from request_coalescing_py.models import Item


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="function")
async def test_app() -> FastAPI:
    async with LifespanManager(app) as manager:
        yield manager.app


@pytest.fixture(scope="function")
async def client(test_app) -> AsyncClient:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client