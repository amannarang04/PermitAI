from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database.session import get_db
from app.services.auth import get_admin_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.configuration import Configuration

router = APIRouter(prefix="/api/admin", tags=["admin"])

class ConfigUpdateRequest(BaseModel):
    value: str

@router.get("/audit-log")
async def get_audit_log(
    application_id: Optional[str] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get audit compliance log entries (Admins only)
    """
    query = db.query(AuditLog)
    
    if application_id:
        # Match application_id string, find corresponding Application.id first
        from app.models.application import Application
        app = db.query(Application).filter(Application.application_id == application_id).first()
        if app:
            query = query.filter(AuditLog.application_id == app.id)
        else:
            return {"logs": []}
            
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
        
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Structure responses
    logs_res = []
    for log in logs:
        app_id_str = None
        if log.application:
            app_id_str = log.application.application_id
            
        logs_res.append({
            "id": log.id,
            "application_id": app_id_str,
            "user_id": log.user_id,
            "username": log.user.username if log.user else None,
            "action": log.action,
            "action_category": log.action_category,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "timestamp": log.timestamp
        })
    return {"logs": logs_res}

@router.get("/config")
async def get_all_configurations(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all dynamic application settings (Admins only)
    """
    return db.query(Configuration).all()

@router.put("/config/{key}")
async def update_configuration(
    key: str,
    payload: ConfigUpdateRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a dynamic setting/threshold in the DB (Admins only)
    """
    config = db.query(Configuration).filter(Configuration.key == key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration setting not found"
        )
        
    # Validate type if set
    if config.value_type == "integer":
        try:
            int(payload.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Value must be a valid integer")
    elif config.value_type == "float":
        try:
            float(payload.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Value must be a valid float")
    elif config.value_type == "boolean":
        if payload.value.lower() not in ("true", "false", "1", "0"):
            raise HTTPException(status_code=400, detail="Value must be a valid boolean")

    config.value = payload.value
    config.updated_by_user_id = current_user.id
    db.commit()
    db.refresh(config)
    
    return {
        "message": f"Successfully updated config key '{key}'",
        "key": config.key,
        "value": config.value
    }
