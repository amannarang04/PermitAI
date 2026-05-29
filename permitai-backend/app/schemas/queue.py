from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.application import ApplicationResponse

class QueueAssignmentResponse(BaseModel):
    id: int
    application_id: int
    queue_name: str
    queue_priority: str
    assigned_to_user_id: Optional[int]
    assigned_at: datetime
    status: str
    completed_at: Optional[datetime]
    completed_by_user_id: Optional[int]
    estimated_completion_time: Optional[datetime]
    actual_completion_time: Optional[datetime]
    application: Optional[ApplicationResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ReassignRequest(BaseModel):
    assigned_to_user_id: int
    reason: Optional[str] = None
