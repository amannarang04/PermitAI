from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.auth import get_supervisor_user
from app.models.user import User
from app.schemas.metrics import (
    MetricsResponse, QueueDetail, BottleneckDetail, TrendResponse, OfficerProductivity
)
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

@router.get("/queue-status", response_model=List[QueueDetail])
async def get_queue_status(
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed metrics breakdown for each queue (pending counts, oldest tasks).
    """
    return MetricsService.get_detailed_queue_status(db)

@router.get("/officer-productivity", response_model=List[OfficerProductivity])
async def get_officer_productivity(
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed productivity breakdown for officers.
    """
    dashboard = MetricsService.get_dashboard_metrics(db)
    return dashboard["officer_productivity"]

@router.get("/bottleneck-analysis", response_model=List[BottleneckDetail])
async def get_bottleneck_analysis(
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Perform bottleneck and processing delay analysis on queues.
    """
    return MetricsService.get_bottleneck_analysis(db)

@router.get("/trends", response_model=TrendResponse)
async def get_metrics_trends(
    days: int = 30,
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Get daily received, approved, and rejected trends over the past N days.
    """
    trends = MetricsService.get_trends(db, days=days)
    return {"trends": trends}
