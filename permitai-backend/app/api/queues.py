from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.session import get_db
from app.services.auth import get_staff_user, get_supervisor_user
from app.models.queue_assignment import QueueAssignment, QueueHistory
from app.models.user import User
from app.models.application import Application
from app.schemas.queue import QueueAssignmentResponse, ReassignRequest
from app.constants.enums import QueueAssignmentStatus

router = APIRouter(prefix="/api/queues", tags=["queues"])

@router.get("/status")
async def get_queue_status(
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Get general count of pending assignments across all queues
    """
    # Group by queue_name
    results = db.query(
        QueueAssignment.queue_name, 
        status.name if hasattr(status := QueueAssignment.status, "name") else QueueAssignment.status,
        from_val := func.count(QueueAssignment.id) if hasattr(from_val := globals().get("func"), "count") else db.query(QueueAssignment).count() # placeholder for count
    )
    # Let's write a simple query
    queues = db.query(QueueAssignment.queue_name).distinct().all()
    status_summary = {}
    for q in queues:
        q_name = q[0]
        pending_count = db.query(QueueAssignment).filter(
            QueueAssignment.queue_name == q_name,
            QueueAssignment.status == QueueAssignmentStatus.PENDING
        ).count()
        in_progress_count = db.query(QueueAssignment).filter(
            QueueAssignment.queue_name == q_name,
            QueueAssignment.status == QueueAssignmentStatus.IN_PROGRESS
        ).count()
        status_summary[q_name] = {
            "pending": pending_count,
            "in_progress": in_progress_count
        }
    return status_summary

@router.get("/{queue_name}", response_model=List[QueueAssignmentResponse])
async def get_queue_assignments(
    queue_name: str,
    status_filter: Optional[str] = QueueAssignmentStatus.PENDING,
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Get all active assignments in a specific queue
    """
    query = db.query(QueueAssignment).filter(
        QueueAssignment.queue_name == queue_name
    )
    if status_filter:
        query = query.filter(QueueAssignment.status == status_filter)
    
    return query.all()

@router.post("/assignments/{assignment_id}/reassign")
async def reassign_application(
    assignment_id: int,
    payload: ReassignRequest,
    current_user: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """
    Reassign an application to another staff officer (Supervisors only)
    """
    assignment = db.query(QueueAssignment).filter(
        QueueAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check target user
    target_user = db.query(User).filter(User.id == payload.assigned_to_user_id).first()
    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user does not exist or is inactive"
        )

    old_user_id = assignment.assigned_to_user_id
    assignment.assigned_to_user_id = target_user.id
    assignment.status = QueueAssignmentStatus.REASSIGNED
    
    # Update active assignment in application
    app = db.query(Application).filter(Application.id == assignment.application_id).first()
    if app:
        app.assigned_to_user_id = target_user.id
        app.assigned_at = datetime.utcnow()
        
    # Log reassign history
    hist = QueueHistory(
        application_id=assignment.application_id,
        from_queue=assignment.queue_name,
        to_queue=assignment.queue_name,
        moved_by_user_id=current_user.id,
        moved_at=datetime.utcnow(),
        reason=payload.reason or f"Manually reassigned from user {old_user_id} to user {target_user.id}"
    )
    db.add(hist)
    
    # Create new queue assignment under same queue name for the new user
    new_assignment = QueueAssignment(
        application_id=assignment.application_id,
        queue_name=assignment.queue_name,
        queue_priority=assignment.queue_priority,
        assigned_to_user_id=target_user.id,
        assigned_at=datetime.utcnow(),
        status=QueueAssignmentStatus.PENDING,
        estimated_completion_time=assignment.estimated_completion_time
    )
    db.add(new_assignment)
    db.commit()
    
    return {
        "message": f"Successfully reassigned to {target_user.full_name or target_user.username}",
        "new_assignment_id": new_assignment.id
    }
