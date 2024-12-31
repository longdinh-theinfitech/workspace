from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from .lookback.routers import lookback


api_router = APIRouter()

api_router.include_router(lookback.router, prefix="/lookback", tags=["lookback"])

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(api_router)
