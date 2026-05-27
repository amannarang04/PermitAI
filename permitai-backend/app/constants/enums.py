from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    SUPERVISOR = "supervisor"
    DIRECTOR = "director"
    ADMIN = "admin"

class ApplicationStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_DOCS = "pending_docs"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"

class ValidationErrorType(str, Enum):
    MISSING_REQUIRED = "missing_required"
    INVALID_FORMAT = "invalid_format"
    BUSINESS_LOGIC = "business_logic"
    FRAUD_FLAG = "fraud_flag"
    DATABASE_MISMATCH = "database_mismatch"

class ValidationErrorSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class QueueAssignmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REASSIGNED = "reassigned"

class QueuePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
