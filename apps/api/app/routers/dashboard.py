from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardStats:
    """Get dashboard statistics."""
    return await DashboardService.get_stats(db)
