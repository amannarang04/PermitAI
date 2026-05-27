from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import os

from app.database.session import get_db
from app.services.auth import get_current_user, get_staff_user
from app.services.storage import StorageService
from app.models.user import User
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.schemas.application import (
    ApplicationResponse, ApplicationDetailResponse, ApplicationListResponse
)
from app.tasks.extraction_tasks import extract_document_async
from app.tasks.notification_tasks import send_approval_email, send_rejection_email, send_missing_documents_email
from app.config import settings
from app.constants.enums import ApplicationStatus

router = APIRouter(prefix="/api/applications", tags=["applications"])

def _get_next_steps(application: Application) -> str:
    status = application.status
    if status == ApplicationStatus.APPROVED:
        return "Download your digital permit copy or pick up the physical copy from the BBMP Municipal Office."
    elif status == ApplicationStatus.REJECTED:
        return "Review the rejection reason, update the application, and resubmit the form."
    elif status == ApplicationStatus.PENDING_DOCS:
        return "Action required: Log in and upload the missing documents requested by the reviewer."
    elif status == ApplicationStatus.FLAGGED:
        return "Your permit application is undergoing a compliance and fraud audit."
    elif status == ApplicationStatus.UNDER_REVIEW:
        return "Your application is currently being evaluated by a staff officer."
    return "Our AI validation systems are currently processing the uploaded form."

# ============================================================================
# CITIZEN ENDPOINTS
# ============================================================================

@router.post("/upload")
async def upload_application(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload permit application form (PDF, JPEG, PNG, max 10MB)
    """
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, JPG, and PNG are allowed."
        )

    # Validate file size
    content = await file.read()
    max_size = settings.S3_MAX_FILE_SIZE
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size allowed is {max_size // (1024*1024)}MB"
        )

    # Generate application ID
    app_id_str = f"PRM-{datetime.utcnow().strftime('%Y')}-{uuid.uuid4().hex[:8].upper()}"

    # Store file in S3/Local storage
    file_path = await StorageService.upload_file(
        file_content=content,
        file_name=file.filename,
        application_id=app_id_str
    )

    # Guess permit type based on filename for initial record creation
    permit_type = "Building"
    fname = file.filename.lower()
    if "electrical" in fname:
        permit_type = "Electrical"
    elif "plumbing" in fname:
        permit_type = "Plumbing"

    # Create application record
    application = Application(
        application_id=app_id_str,
        citizen_id=current_user.id,
        status=ApplicationStatus.RECEIVED,
        permit_type=permit_type,
        original_file_name=file.filename,
        original_file_path=file_path,
        original_file_size=len(content),
        original_file_type=file.content_type.split("/")[1],
        city="bangalore"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # Trigger async extraction task
    # We fallback to sync execution if celery/redis tasks are not running
    try:
        extract_document_async.delay(application.id)
    except Exception:
        # Synch fallback for local test stability
        from app.tasks.extraction_tasks import run_extraction_sync
        run_extraction_sync(application.id)

    # Log action
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="uploaded",
        action_category="write",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "application_id": application.application_id,
        "status": application.status,
        "quality_score": application.quality_score,
        "message": "Application received. Processing in background..."
    }

@router.get("/track/{application_id}")
async def track_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track application status history (Citizens)
    """
    application = db.query(Application).filter(
        Application.application_id == application_id,
        Application.citizen_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Calculate processing days
    if application.decided_at:
        processing_days = (application.decided_at - application.submitted_at).days
    else:
        processing_days = (datetime.utcnow() - application.submitted_at).days

    # Build timeline list
    timeline = []
    if application.submitted_at:
        timeline.append({"date": application.submitted_at, "event": "Application Received"})
    if application.processed_at:
        timeline.append({"date": application.processed_at, "event": "Data Validated"})
    if application.assigned_at:
        timeline.append({"date": application.assigned_at, "event": "Assigned for Review"})
    if application.reviewed_at:
        timeline.append({"date": application.reviewed_at, "event": "Under Review"})
    if application.decided_at:
        event_name = "APPROVED" if application.status == ApplicationStatus.APPROVED else "REJECTED"
        timeline.append({"date": application.decided_at, "event": event_name})

    return {
        "application_id": application.application_id,
        "status": application.status,
        "quality_score": application.quality_score,
        "processing_days": max(0, processing_days),
        "timeline": timeline,
        "next_steps": _get_next_steps(application)
    }

@router.post("/{application_id}/resubmit")
async def resubmit_application(
    application_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resubmit application with correct/missing documents
    """
    application = db.query(Application).filter(
        Application.application_id == application_id,
        Application.citizen_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.status not in [ApplicationStatus.PENDING_DOCS, ApplicationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resubmit in current status"
        )

    content = await file.read()
    file_path = await StorageService.upload_file(
        file_content=content,
        file_name=file.filename,
        application_id=application.application_id
    )

    # Reset status
    application.original_file_path = file_path
    application.original_file_name = file.filename
    application.original_file_size = len(content)
    application.original_file_type = file.content_type.split("/")[1]
    application.status = ApplicationStatus.RECEIVED
    application.quality_score = None
    application.submitted_at = datetime.utcnow()
    application.processed_at = None
    application.decided_at = None

    db.commit()

    # Re-trigger extraction
    try:
        extract_document_async.delay(application.id)
    except Exception:
        from app.tasks.extraction_tasks import run_extraction_sync
        run_extraction_sync(application.id)

    # Log action
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="resubmitted",
        action_category="write",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "application_id": application.application_id,
        "status": application.status,
        "message": "Resubmitted successfully. Processing in background..."
    }

# ============================================================================
# STAFF ENDPOINTS
# ============================================================================

@router.get("/queue/my-queue")
async def get_my_queue(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications assigned to the logged-in staff member
    """
    query = db.query(Application).filter(
        Application.assigned_to_user_id == current_user.id
    )

    if status_filter:
        query = query.filter(Application.status == status_filter)

    total = query.count()
    applications = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "applications": [
            ApplicationResponse.model_validate(app) for app in applications
        ]
    }

@router.get("/{application_id}/details", response_model=ApplicationDetailResponse)
async def get_application_details(
    application_id: str,
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Get full application details for evaluation
    """
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Log viewing action to compliance audit log
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="viewed",
        action_category="read",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return application

@router.post("/{application_id}/approve")
async def approve_application(
    application_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Approve building permit application
    """
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.status == ApplicationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already approved"
        )

    # Approve
    application.status = ApplicationStatus.APPROVED
    application.decided_at = datetime.utcnow()
    application.approved_notes = notes

    # Generate permit number
    permit_number = f"BP-{datetime.utcnow().strftime('%Y')}-{uuid.uuid4().hex[:8].upper()}"

    db.commit()

    # Trigger notification
    try:
        send_approval_email.delay(application.id, permit_number)
    except Exception:
        # Sync fallback
        from app.services.notification import NotificationService
        NotificationService.send_approval_email(db, application.id, permit_number)

    # Log action
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="approved",
        action_category="write",
        details={"notes": notes, "permit_number": permit_number},
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "application_id": application.application_id,
        "status": application.status,
        "permit_number": permit_number
    }

@router.post("/{application_id}/reject")
async def reject_application(
    application_id: str,
    rejection_reason: str,
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Reject building permit application
    """
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.status == ApplicationStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already rejected"
        )

    # Reject
    application.status = ApplicationStatus.REJECTED
    application.decided_at = datetime.utcnow()
    application.rejected_reason = rejection_reason

    db.commit()

    # Trigger notification
    try:
        send_rejection_email.delay(application.id, rejection_reason)
    except Exception:
        # Sync fallback
        from app.services.notification import NotificationService
        NotificationService.send_rejection_email(db, application.id, rejection_reason)

    # Log action
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="rejected",
        action_category="write",
        details={"reason": rejection_reason},
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "application_id": application.application_id,
        "status": application.status
    }

@router.post("/{application_id}/request-documents")
async def request_more_documents(
    application_id: str,
    missing_documents: List[str],
    current_user: User = Depends(get_staff_user),
    db: Session = Depends(get_db)
):
    """
    Request missing documents from citizen
    """
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Update status
    application.status = ApplicationStatus.PENDING_DOCS

    db.commit()

    # Trigger notification
    try:
        send_missing_documents_email.delay(application.id, missing_documents)
    except Exception:
        # Sync fallback
        from app.services.notification import NotificationService
        NotificationService.send_missing_documents_email(db, application.id, missing_documents)

    # Log action
    log = AuditLog(
        application_id=application.id,
        user_id=current_user.id,
        action="requested_documents",
        action_category="write",
        details={"missing_documents": missing_documents},
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "application_id": application.application_id,
        "status": application.status
    }
