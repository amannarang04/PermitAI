from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.database.session import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.models.notification import InAppNotification
from app.schemas.notification import InAppNotificationResponse, NotificationPreferencesUpdate

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("", response_model=List[InAppNotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get in-app notifications for the logged-in user
    """
    notifications = db.query(InAppNotification).filter(
        InAppNotification.user_id == current_user.id
    ).order_by(InAppNotification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications

@router.patch("/{notification_id}/read", response_model=InAppNotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark in-app notification as read
    """
    notification = db.query(InAppNotification).filter(
        InAppNotification.id == notification_id,
        InAppNotification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
        
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

@router.patch("/preferences")
async def update_preferences(
    preferences: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification preferences (email, sms, in_app)
    """
    current_user.notification_preferences = preferences.model_dump()
    db.commit()
    db.refresh(current_user)
    return {"message": "Preferences updated successfully", "preferences": current_user.notification_preferences}
