from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import random

from app.models.application import Application
from app.models.queue_assignment import QueueAssignment, QueueHistory
from app.models.user import User
from app.constants.enums import QueueAssignmentStatus, QueuePriority, ApplicationStatus, UserRole
from app.services.validation import ValidationService

class RoutingService:
    @staticmethod
    def route_application(db: Session, app_id: int) -> QueueAssignment:
        """
        Routes application to a specific queue and history log based on status, permit_type,
        and cost thresholds. Assigns to staff officers in round-robin/random.
        """
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise ValueError("Application not found")

        # 1. Clear any pending queue assignments
        db.query(QueueAssignment).filter(
            QueueAssignment.application_id == app.id,
            QueueAssignment.status == QueueAssignmentStatus.PENDING
        ).delete()
        db.commit()

        # 2. Determine Queue Name and Priority
        queue_name = "general_staff_review"
        priority = QueuePriority.MEDIUM

        cost_threshold = ValidationService.get_config(db, "auto_approval_threshold")  # default 5 Lakhs
        cost_val = float(app.estimated_cost) if app.estimated_cost is not None else 0.0

        if app.status == ApplicationStatus.FLAGGED:
            queue_name = "flagged_fraud_review"
            priority = QueuePriority.CRITICAL
        elif app.status == ApplicationStatus.PENDING_DOCS:
            queue_name = "citizen_document_pending"
            priority = QueuePriority.MEDIUM
        elif app.status == ApplicationStatus.APPROVED:
            queue_name = "completed_approvals"
            priority = QueuePriority.LOW
        elif app.status == ApplicationStatus.REJECTED:
            queue_name = "completed_rejections"
            priority = QueuePriority.LOW
        elif cost_val <= cost_threshold and app.quality_score and app.quality_score >= 90:
            # Low cost, high quality score, no flags -> supervisor auto approval queue
            queue_name = "supervisor_auto_approval"
            priority = QueuePriority.LOW
        else:
            # Route by permit type
            ptype = (app.permit_type or "").lower()
            if "electrical" in ptype:
                queue_name = "electrical_review"
            elif "plumbing" in ptype:
                queue_name = "plumbing_review"
            elif "building" in ptype:
                queue_name = "building_engineer_review"
            else:
                queue_name = "officer_general_review"

            # Route cost over 50 Lakhs directly to critical Director queue
            if cost_val > 5000000.0:
                queue_name = "director_high_value_review"
                priority = QueuePriority.HIGH

        # 3. Find suitable staff user for assignment
        assigned_user_id = None
        department_map = {
            "electrical_review": "Electrical",
            "plumbing_review": "Plumbing",
            "building_engineer_review": "Building",
        }
        dept_filter = department_map.get(queue_name)

        query = db.query(User).filter(User.is_active == True)
        if queue_name == "director_high_value_review":
            query = query.filter(User.role == UserRole.DIRECTOR)
        elif queue_name == "supervisor_auto_approval":
            query = query.filter(User.role == UserRole.SUPERVISOR)
        elif queue_name == "flagged_fraud_review":
            query = query.filter(User.role.in_([UserRole.SUPERVISOR, UserRole.DIRECTOR, UserRole.ADMIN]))
        elif dept_filter:
            query = query.filter(User.department == dept_filter, User.role == UserRole.OFFICER)
        else:
            query = query.filter(User.role == UserRole.OFFICER)

        staff_list = query.all()
        if staff_list:
            # Randomly select a staff member to distribute load
            selected_staff = random.choice(staff_list)
            assigned_user_id = selected_staff.id

        # 4. Create Queue Assignment
        eta = datetime.utcnow() + timedelta(days=2 if priority == QueuePriority.CRITICAL else (5 if priority == QueuePriority.HIGH else 7))
        
        assignment = QueueAssignment(
            application_id=app.id,
            queue_name=queue_name,
            queue_priority=priority,
            assigned_to_user_id=assigned_user_id,
            assigned_at=datetime.utcnow(),
            status=QueueAssignmentStatus.PENDING,
            estimated_completion_time=eta
        )
        db.add(assignment)

        # Update application's assigned user
        app.assigned_to_user_id = assigned_user_id
        app.assigned_at = datetime.utcnow()
        if app.status == ApplicationStatus.PROCESSING:
            app.status = ApplicationStatus.UNDER_REVIEW

        # 5. Log in Queue History
        hist = QueueHistory(
            application_id=app.id,
            from_queue=None,
            to_queue=queue_name,
            moved_by_user_id=None,
            moved_at=datetime.utcnow(),
            reason="Automated routing based on AI validation results"
        )
        db.add(hist)

        db.commit()
        db.refresh(assignment)
        return assignment
