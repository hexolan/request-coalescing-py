import asyncio

from fastapi import FastAPI

from request_coalescing_py.database import DatabaseRepo
from request_coalescing_py.coalescer import CoalescingRepo
from request_coalescing_py.routes import router

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # initialise metrics
    app.state.DEFAULT_METRICS = {"requests": 0, "db_calls": 0}
    app.state.metrics = app.state.DEFAULT_METRICS.copy()
    
    # initilise DB repository
    app.state.repo = DatabaseRepo(app=app)
    await app.state.repo.start_db()

    # initialise worker and coalescing repo
    app.state.coalescer = CoalescingRepo(repo=app.state.repo)
    asyncio.create_task(app.state.coalescer.process_queue())


@app.on_event("shutdown")
async def shutdown_event():
    # close DB connection
    await app.state.repo.stop_db()


app.include_router(router)