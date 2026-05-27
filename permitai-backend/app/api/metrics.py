from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth import get_supervisor_user
from app.models.user import User
from app.schemas.metrics import MetricsResponse
from app.services.metrics import MetricsService

router = APIRouter(prefix="/api/admin/metrics", tags=["metrics"])

@router.get("/dashboard", response_model=MetricsResponse)
async def get_metrics_dashboard(
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics breakdown for supervisors and directors.
    """
    return MetricsService.get_dashboard_metrics(db)
