from fastapi import APIRouter, Request, HTTPException

from request_coalescing_py.models import Item

router = APIRouter()


@router.get("/metrics")
def view_metrics(request: Request) -> dict:
    return request.app.state.metrics


@router.post("/metrics")
def view_and_reset_metrics(request: Request) -> dict:
    metrics = request.app.state.metrics
    request.app.state.metrics = request.app.state.DEFAULT_METRICS.copy()
    return metrics


@router.get("/standard/{item_id}")
async def get_standard_route(request: Request, item_id: int) -> Item:
    request.app.state.metrics["requests"] += 1

    item = await request.app.state.repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not Found")
    
    return item


@router.get("/coalesced/{item_id}")
async def get_coalesced_route(request: Request, item_id: int) -> Item:
    request.app.state.metrics["requests"] += 1

    item_future = await request.app.state.coalescer.get_by_id(item_id)
    item = await item_future
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not Found")
    
    return item