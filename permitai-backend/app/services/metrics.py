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

    @staticmethod
    def get_detailed_queue_status(db: Session) -> list:
        """
        Returns list of detailed status for each queue
        """
        now = datetime.utcnow()
        queues = ["general_staff_review", "citizen_document_pending", "supervisor_auto_approval", "flagged_fraud_review", "electrical_review", "plumbing_review", "building_engineer_review", "officer_general_review", "director_high_value_review"]
        
        results = []
        for q_name in queues:
            pending_assignments = db.query(QueueAssignment).filter(
                QueueAssignment.queue_name == q_name,
                QueueAssignment.status == QueueAssignmentStatus.PENDING
            ).all()
            
            pending_count = len(pending_assignments)
            
            oldest_task_days = 0.0
            average_wait_hours = 0.0
            
            if pending_count > 0:
                oldest_assigned = min(qa.assigned_at for qa in pending_assignments if qa.assigned_at)
                oldest_task_days = round((now - oldest_assigned).total_seconds() / 86400.0, 2)
                
                total_wait_hours = sum((now - qa.assigned_at).total_seconds() / 3600.0 for qa in pending_assignments if qa.assigned_at)
                average_wait_hours = round(total_wait_hours / pending_count, 1)
                
            results.append({
                "queue_name": q_name,
                "pending_count": pending_count,
                "oldest_task_days": oldest_task_days,
                "average_wait_hours": average_wait_hours
            })
            
        return results

    @staticmethod
    def get_bottleneck_analysis(db: Session) -> list:
        """
        Performs bottleneck analysis on all queues
        """
        detailed_queues = MetricsService.get_detailed_queue_status(db)
        
        results = []
        for q in detailed_queues:
            q_name = q["queue_name"]
            backlog = q["pending_count"]
            
            # Calculate average processing time for completed assignments in hours
            completed_assignments = db.query(QueueAssignment).filter(
                QueueAssignment.queue_name == q_name,
                QueueAssignment.status == QueueAssignmentStatus.COMPLETED,
                QueueAssignment.completed_at.isnot(None),
                QueueAssignment.assigned_at.isnot(None)
            ).all()
            
            avg_proc_time = 0.0
            if completed_assignments:
                total_hours = sum((qa.completed_at - qa.assigned_at).total_seconds() / 3600.0 for qa in completed_assignments)
                avg_proc_time = round(total_hours / len(completed_assignments), 1)
                
            # A queue is flagged as bottleneck if backlog > 5 or avg wait time > 24 hours
            is_bottleneck = backlog > 5 or q["average_wait_hours"] > 24.0
            
            # Severity calculation
            if backlog >= 10 or q["average_wait_hours"] > 72.0:
                severity = "critical"
            elif backlog >= 5 or q["average_wait_hours"] > 24.0:
                severity = "high"
            elif backlog >= 2:
                severity = "medium"
            else:
                severity = "low"
                
            results.append({
                "queue_name": q_name,
                "backlog_count": backlog,
                "average_processing_time_hours": avg_proc_time,
                "is_bottleneck": is_bottleneck,
                "severity": severity
            })
            
        return results

    @staticmethod
    def get_trends(db: Session, days: int = 30) -> list:
        """
        Returns received/approved/rejected counts grouped by date for last N days
        """
        from datetime import timedelta
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # We fetch all applications decided/submitted in the last N days
        # And aggregate them in python to be sqlite/postgres compatible
        apps = db.query(Application).filter(
            (Application.submitted_at >= start_date) | 
            (Application.decided_at >= start_date)
        ).all()
        
        trend_map = {}
        # Pre-populate dates
        for i in range(days):
            d_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            trend_map[d_str] = {"received": 0, "approved": 0, "rejected": 0}
            
        for app in apps:
            if app.submitted_at and app.submitted_at >= start_date:
                sub_str = app.submitted_at.strftime("%Y-%m-%d")
                if sub_str in trend_map:
                    trend_map[sub_str]["received"] += 1
            if app.decided_at and app.decided_at >= start_date:
                dec_str = app.decided_at.strftime("%Y-%m-%d")
                if dec_str in trend_map:
                    if app.status == ApplicationStatus.APPROVED:
                        trend_map[dec_str]["approved"] += 1
                    elif app.status == ApplicationStatus.REJECTED:
                        trend_map[dec_str]["rejected"] += 1
                        
        results = []
        for d_str, counts in sorted(trend_map.items()):
            results.append({
                "date": d_str,
                "received": counts["received"],
                "approved": counts["approved"],
                "rejected": counts["rejected"]
            })
            
        return results
