from sqlalchemy.orm import Session
from datetime import datetime, time
from sqlalchemy import func

from app.models.application import Application
from app.models.queue_assignment import QueueAssignment
from app.models.user import User
from app.constants.enums import ApplicationStatus, QueueAssignmentStatus, UserRole

class MetricsService:
    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        """
        Calculates all dashboard metrics for supervisors and directors.
        """
        now = datetime.utcnow()
        today_start = datetime.combine(now.date(), time.min)
        month_start = datetime(now.year, now.month, 1)

        # 1. Today's counters
        today_received = db.query(Application).filter(
            Application.submitted_at >= today_start
        ).count()

        today_processed = db.query(Application).filter(
            Application.processed_at >= today_start
        ).count()

        today_pending = db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.RECEIVED,
                ApplicationStatus.PROCESSING,
                ApplicationStatus.UNDER_REVIEW
            ])
        ).count()

        # 2. This month's counters
        month_total = db.query(Application).filter(
            Application.submitted_at >= month_start
        ).count()

        month_approved = db.query(Application).filter(
            Application.status == ApplicationStatus.APPROVED,
            Application.decided_at >= month_start
        ).count()

        month_rejected = db.query(Application).filter(
            Application.status == ApplicationStatus.REJECTED,
            Application.decided_at >= month_start
        ).count()

        month_pending = db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.RECEIVED,
                ApplicationStatus.PROCESSING,
                ApplicationStatus.UNDER_REVIEW
            ]),
            Application.submitted_at >= month_start
        ).count()

        # Calculate average days for decided applications this month
        decided_apps = db.query(Application).filter(
            Application.decided_at >= month_start,
            Application.submitted_at.isnot(None),
            Application.decided_at.isnot(None)
        ).all()

        total_days = 0.0
        for app in decided_apps:
            delta = app.decided_at - app.submitted_at
            total_days += max(0.1, delta.total_seconds() / 86400.0)
        
        avg_days = round(total_days / len(decided_apps), 1) if decided_apps else 0.0

        # 3. Queue status breakdown
        ready_for_approval = db.query(QueueAssignment).filter(
            QueueAssignment.queue_name == "supervisor_auto_approval",
            QueueAssignment.status == QueueAssignmentStatus.PENDING
        ).count()

        pending_documents = db.query(QueueAssignment).filter(
            QueueAssignment.queue_name == "citizen_document_pending",
            QueueAssignment.status == QueueAssignmentStatus.PENDING
        ).count()

        under_review = db.query(QueueAssignment).filter(
            QueueAssignment.status == QueueAssignmentStatus.PENDING,
            QueueAssignment.queue_name.notin_([
                "supervisor_auto_approval",
                "citizen_document_pending",
                "flagged_fraud_review"
            ])
        ).count()

        flagged = db.query(QueueAssignment).filter(
            QueueAssignment.queue_name == "flagged_fraud_review",
            QueueAssignment.status == QueueAssignmentStatus.PENDING
        ).count()

        # 4. Officer productivity
        # Find all staff members (officers, supervisors)
        staff_users = db.query(User).filter(
            User.role.in_([UserRole.OFFICER, UserRole.SUPERVISOR])
        ).all()

        officer_productivity = []
        for staff in staff_users:
            # Approvals today by this user
            approvals_today = db.query(Application).filter(
                Application.status == ApplicationStatus.APPROVED,
                Application.decided_at >= today_start,
                Application.assigned_to_user_id == staff.id
            ).count()

            # Average completion time for assignments completed by this staff member (in hours)
            completed_assignments = db.query(QueueAssignment).filter(
                QueueAssignment.completed_by_user_id == staff.id,
                QueueAssignment.status == QueueAssignmentStatus.COMPLETED,
                QueueAssignment.completed_at.isnot(None),
                QueueAssignment.assigned_at.isnot(None)
            ).all()

            total_hours = 0.0
            for qa in completed_assignments:
                delta = qa.completed_at - qa.assigned_at
                total_hours += max(0.1, delta.total_seconds() / 3600.0)
            
            avg_time = round(total_hours / len(completed_assignments), 1) if completed_assignments else 0.0

            officer_productivity.append({
                "name": staff.full_name or staff.username,
                "approvals_today": approvals_today,
                "avg_time": avg_time
            })

        # If officer productivity is empty, provide a default mock officer to avoid empty UI charts
        if not officer_productivity:
            officer_productivity.append({
                "name": "Unassigned System",
                "approvals_today": 0,
                "avg_time": 0.0
            })

        return {
            "today": {
                "received": today_received,
                "processed": today_processed,
                "pending": today_pending
            },
            "this_month": {
                "total": month_total,
                "approved": month_approved,
                "rejected": month_rejected,
                "pending": month_pending,
                "avg_days": avg_days
            },
            "queue_status": {
                "ready_for_approval": ready_for_approval,
                "pending_documents": pending_documents,
                "under_review": under_review,
                "flagged": flagged
            },
            "officer_productivity": officer_productivity
        }
