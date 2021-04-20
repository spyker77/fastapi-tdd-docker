from fastapi import APIRouter

from .endpoints import ping, summaries

api_router_v2 = APIRouter(prefix="/api/v2", tags=["v2"])
api_router_v2.include_router(ping.router)
api_router_v2.include_router(summaries.router, prefix="/summaries")
