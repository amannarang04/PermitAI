import logging
from typing import List
from app.tasks.celery_app import celery_app
from app.database.session import SessionLocal
from app.services.notification import NotificationService

logger = logging.getLogger("permitai.tasks")

@celery_app.task(name="app.tasks.notification_tasks.send_approval_email")
def send_approval_email(app_db_id: int, permit_number: str):
    """Async task to send permit approval email notification"""
    db = SessionLocal()
    try:
        NotificationService.send_approval_email(db, app_db_id, permit_number)
    except Exception as e:
        logger.exception(f"Failed to send approval email for application ID {app_db_id}: {e}")
    finally:
        db.close()

@celery_app.task(name="app.tasks.notification_tasks.send_rejection_email")
def send_rejection_email(app_db_id: int, rejection_reason: str):
    """Async task to send permit rejection email notification"""
    db = SessionLocal()
    try:
        NotificationService.send_rejection_email(db, app_db_id, rejection_reason)
    except Exception as e:
        logger.exception(f"Failed to send rejection email for application ID {app_db_id}: {e}")
    finally:
        db.close()

@celery_app.task(name="app.tasks.notification_tasks.send_missing_documents_email")
def send_missing_documents_email(app_db_id: int, missing_docs: List[str]):
    """Async task to send missing documents email notification"""
    db = SessionLocal()
    try:
        NotificationService.send_missing_documents_email(db, app_db_id, missing_docs)
    except Exception as e:
        logger.exception(f"Failed to send missing documents email for application ID {app_db_id}: {e}")
    finally:
        db.close()
