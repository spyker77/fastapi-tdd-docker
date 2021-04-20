from fastapi import APIRouter

from .endpoints import ping, summaries

api_router_v1 = APIRouter(prefix="/api/v1", tags=["v1"], deprecated=True)
api_router_v1.include_router(ping.router)
api_router_v1.include_router(summaries.router, prefix="/summaries")
