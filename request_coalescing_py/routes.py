from fastapi import APIRouter, Request, HTTPException

from request_coalescing_py.models import Item

router = APIRouter()


@router.get("/metrics")
def view_metrics(request: Request) -> dict:
    """View the metrics (number of requests and database calls processed)"""
    return request.app.state.metrics


@router.post("/metrics")
def view_and_reset_metrics(request: Request) -> dict:
    """View and reset the metrics"""
    metrics = request.app.state.metrics
    request.app.state.metrics = request.app.state.DEFAULT_METRICS.copy()
    return metrics


@router.get("/standard/{item_id}")
async def get_standard_route(request: Request, item_id: int) -> Item:
    """Get an item by a specified id.

    Requests to this route are not coalesced. Directly calls
    the database repository to get items.

    Args:
        request (Request): Used to access the metrics object in app state.
        item_id (int): The requested item id.

    Raises:
        HTTPException: When the requested item is not found.

    Returns:
        Item: Details of the requested item.

    """
    request.app.state.metrics["requests"] += 1

    item = await request.app.state.repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not Found")
    
    return item


@router.get("/coalesced/{item_id}")
async def get_coalesced_route(request: Request, item_id: int) -> Item:
    """Get an item by a specified id.

    This route will request a future from the coalescing 
    repository and await the resulting response of that future,
    pending being processed by the task queue.

    Requests to this route should reduce the overall number
    of database calls being made (should requests be made
    simultaneously).

    Args:
        request (Request): Used to access the metrics object in app state.
        item_id (int): The requested item id.

    Raises:
        HTTPException: When the requested item is not found.

    Returns:
        Item: Details of the requested item.

    """
    request.app.state.metrics["requests"] += 1

    item_future = await request.app.state.coalescer.get_by_id(item_id)
    item = await item_future
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not Found")
    
    return item