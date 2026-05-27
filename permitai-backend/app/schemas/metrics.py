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
