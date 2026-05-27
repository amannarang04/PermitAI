from pydantic import BaseModel
from typing import List

class TodayMetrics(BaseModel):
    received: int
    processed: int
    pending: int

class MonthMetrics(BaseModel):
    total: int
    approved: int
    rejected: int
    pending: int
    avg_days: float

class QueueStatusMetrics(BaseModel):
    ready_for_approval: int
    pending_documents: int
    under_review: int
    flagged: int

class OfficerProductivity(BaseModel):
    name: str
    approvals_today: int
    avg_time: float

class MetricsResponse(BaseModel):
    today: TodayMetrics
    this_month: MonthMetrics
    queue_status: QueueStatusMetrics
    officer_productivity: List[OfficerProductivity]

class QueueDetail(BaseModel):
    queue_name: str
    pending_count: int
    oldest_task_days: float
    average_wait_hours: float

class BottleneckDetail(BaseModel):
    queue_name: str
    backlog_count: int
    average_processing_time_hours: float
    is_bottleneck: bool
    severity: str  # 'low', 'medium', 'high', 'critical'

class TrendPoint(BaseModel):
    date: str  # YYYY-MM-DD
    received: int
    approved: int
    rejected: int

class TrendResponse(BaseModel):
    trends: List[TrendPoint]
