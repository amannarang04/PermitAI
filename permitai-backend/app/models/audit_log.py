from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)
    action_category = Column(String(50), nullable=True)
    
    details = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    application = relationship("Application", back_populates="audit_logs")
    user = relationship("User")

    __table_args__ = (
        Index("idx_audit_application_id", "application_id"),
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_timestamp", "timestamp"),
    )


class ApiActivityLog(Base):
    __tablename__ = "api_activity_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    endpoint = Column(String(255), nullable=True, index=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index("idx_api_act_user_id", "user_id"),
        Index("idx_api_act_timestamp", "timestamp"),
        Index("idx_api_act_endpoint", "endpoint"),
    )
