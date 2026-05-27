import logging
from app.tasks.celery_app import celery_app
from app.database.session import SessionLocal
from app.services.extraction import ExtractionService
from app.services.validation import ValidationService
from app.services.routing import RoutingService
from app.services.notification import NotificationService
from app.models.application import Application
from app.constants.enums import ApplicationStatus

logger = logging.getLogger("permitai.tasks")

def run_extraction_sync(app_db_id: int) -> bool:
    """
    Synchronous processing helper that runs extraction, validation,
    routing, and emails in a single database session context.
    """
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == app_db_id).first()
        if not app:
            logger.error(f"Application ID {app_db_id} not found in DB.")
            return False

        app.status = ApplicationStatus.PROCESSING
        db.commit()

        # 1. Claude Vision Extraction
        extraction_res = ExtractionService.extract_from_document(
            app.original_file_path, 
            app.original_file_type
        )
        
        if not extraction_res or not extraction_res.get("success"):
            logger.error(f"AI extraction failed for Application ID {app_db_id}")
            app.status = ApplicationStatus.RECEIVED
            db.commit()
            return False

        extracted_data = extraction_res["data"]
        
        # 2. Run validations and fraud checks
        app = ValidationService.validate_application(db, app.id, extracted_data)

        # 3. Route application to queues
        RoutingService.route_application(db, app.id)

        # 4. Trigger Email Notification
        NotificationService.send_received_email(db, app.id)
        
        logger.info(f"Successfully processed and routed application {app.application_id}")
        return True
    except Exception as e:
        logger.exception(f"Unhandled error in extraction task for app {app_db_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()

@celery_app.task(name="app.tasks.extraction_tasks.extract_document_async")
def extract_document_async(app_db_id: int):
    """
    Asynchronous Celery wrapper task for document extraction
    """
    return run_extraction_sync(app_db_id)
