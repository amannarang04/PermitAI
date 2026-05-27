from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InAppNotificationResponse(BaseModel):
    id: int
    user_id: int
    application_id: Optional[str]
    title: str
    message: str
    is_read: bool
    notification_type: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationPreferencesUpdate(BaseModel):
    email: bool
    sms: bool
    in_app: bool
