from fastapi import APIRouter

from .endpoints import ping, summaries, users

api_router_v2 = APIRouter(prefix="/api/v2")
api_router_v2.include_router(ping.router)
api_router_v2.include_router(summaries.router)
api_router_v2.include_router(users.router)
