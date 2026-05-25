from fastapi import APIRouter

from .dashboard import router as dashboard_router

statistics_router = APIRouter()
statistics_router.include_router(dashboard_router, prefix="", tags=["统计模块"])

__all__ = ["statistics_router"]