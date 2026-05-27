from app.database.db import Base
from app.models.user import User, UserSession
from app.models.application import Application, ApplicationDocument
from app.models.validation_error import ValidationError, FraudIndicator
from app.models.queue_assignment import QueueAssignment, QueueHistory
from app.models.audit_log import AuditLog, ApiActivityLog
from app.models.configuration import Configuration
from app.models.notification import InAppNotification

# This allows importing all models from app.models, and registers them with Base.metadata
__all__ = [
    "Base",
    "User",
    "UserSession",
    "Application",
    "ApplicationDocument",
    "ValidationError",
    "FraudIndicator",
    "QueueAssignment",
    "QueueHistory",
    "AuditLog",
    "ApiActivityLog",
    "Configuration",
    "InAppNotification"
]

