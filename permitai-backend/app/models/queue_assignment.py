from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base
from app.constants.enums import QueueAssignmentStatus, QueuePriority

class QueueAssignment(Base):
    __tablename__ = "queue_assignments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    queue_name = Column(String(100), nullable=False, index=True)
    queue_priority = Column(String(50), default=QueuePriority.MEDIUM)
    
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    status = Column(String(50), default=QueueAssignmentStatus.PENDING, index=True)
    
    completed_at = Column(DateTime, nullable=True)
    completed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    estimated_completion_time = Column(DateTime, nullable=True)
    actual_completion_time = Column(DateTime, nullable=True)

    # Relationships
    application = relationship("Application", back_populates="queue_assignments")
    assigned_user = relationship("User", foreign_keys=[assigned_to_user_id])
    completed_user = relationship("User", foreign_keys=[completed_by_user_id])

    __table_args__ = (
        Index("idx_queue_name", "queue_name"),
        Index("idx_queue_assigned_to_user", "assigned_to_user_id"),
        Index("idx_queue_app_id", "application_id"),
        Index("idx_queue_status", "status"),
    )


class QueueHistory(Base):
    __tablename__ = "queue_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    from_queue = Column(String(100), nullable=True)
    to_queue = Column(String(100), nullable=True)
    
    moved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moved_at = Column(DateTime, default=datetime.utcnow)
    
    reason = Column(Text, nullable=True)

    # Relationships
    application = relationship("Application")
    moved_by_user = relationship("User")

    __table_args__ = (
        Index("idx_q_hist_application_id", "application_id"),
    )
