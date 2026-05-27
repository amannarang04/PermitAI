from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base
from app.constants.enums import ValidationErrorSeverity, RiskLevel

class ValidationError(Base):
    __tablename__ = "validation_errors"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    field_name = Column(String(100), nullable=True)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    error_severity = Column(String(50), default=ValidationErrorSeverity.WARNING)
    
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="validation_errors")

    __table_args__ = (
        Index("idx_val_err_application_id", "application_id"),
        Index("idx_val_err_type", "error_type"),
    )


class FraudIndicator(Base):
    __tablename__ = "fraud_indicators"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    indicator_type = Column(String(100), nullable=True)
    indicator_description = Column(Text, nullable=True)
    risk_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    risk_level = Column(String(50), default=RiskLevel.LOW)
    
    recommendation = Column(String(255), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="fraud_indicators")

    __table_args__ = (
        Index("idx_fraud_application_id", "application_id"),
        Index("idx_fraud_risk_level", "risk_level"),
    )
