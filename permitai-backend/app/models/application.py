from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, Index, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base
from app.constants.enums import ApplicationStatus

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), unique=True, nullable=False, index=True)
    
    citizen_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default=ApplicationStatus.RECEIVED, index=True)
    
    quality_score = Column(Integer, nullable=True, index=True)
    extraction_confidence = Column(Numeric(3, 2), nullable=True)

    # APPLICANT INFORMATION
    applicant_name = Column(String(255), nullable=True)
    applicant_email = Column(String(255), nullable=True)
    applicant_phone = Column(String(20), nullable=True)
    applicant_address_line1 = Column(String(255), nullable=True)
    applicant_address_line2 = Column(String(255), nullable=True)
    applicant_address_city = Column(String(100), nullable=True)
    applicant_address_state = Column(String(100), nullable=True)
    applicant_address_zip = Column(String(20), nullable=True)
    applicant_id_type = Column(String(50), nullable=True)
    applicant_id_number = Column(String(100), nullable=True)

    # PROPERTY INFORMATION
    property_address_line1 = Column(String(255), nullable=True)
    property_address_line2 = Column(String(255), nullable=True)
    property_address_city = Column(String(100), nullable=True)
    property_address_state = Column(String(100), nullable=True)
    property_address_zip = Column(String(20), nullable=True)
    property_ward_number = Column(String(20), nullable=True)
    property_size = Column(Numeric(10, 2), nullable=True)
    property_size_unit = Column(String(20), nullable=True)
    property_current_use = Column(String(100), nullable=True)
    property_proposed_use = Column(String(100), nullable=True)
    property_ownership_type = Column(String(50), nullable=True)

    # PROJECT INFORMATION
    permit_type = Column(String(50), nullable=False, index=True)
    project_description = Column(Text, nullable=True)
    project_scope = Column(String(255), nullable=True)
    estimated_cost = Column(Numeric(15, 2), nullable=True)
    estimated_cost_currency = Column(String(10), default="INR")
    construction_area = Column(Numeric(10, 2), nullable=True)
    construction_area_unit = Column(String(20), nullable=True)

    # Timeline
    project_start_date = Column(Date, nullable=True)
    project_end_date = Column(Date, nullable=True)

    # CONTRACTOR INFORMATION
    contractor_name = Column(String(255), nullable=True)
    contractor_license_number = Column(String(100), nullable=True)
    contractor_phone = Column(String(20), nullable=True)
    contractor_email = Column(String(255), nullable=True)
    contractor_address = Column(Text, nullable=True)

    # ENGINEER/ARCHITECT
    engineer_name = Column(String(255), nullable=True)
    engineer_license_number = Column(String(100), nullable=True)
    architect_name = Column(String(255), nullable=True)
    architect_license_number = Column(String(100), nullable=True)

    # FILE INFORMATION
    original_file_name = Column(String(255), nullable=True)
    original_file_path = Column(String(500), nullable=True)
    original_file_size = Column(Integer, nullable=True)
    original_file_type = Column(String(50), nullable=True)

    # OCR/Extraction Info
    extracted_text = Column(Text, nullable=True)
    extraction_method = Column(String(50), nullable=True)

    # WORKFLOW INFORMATION
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    received_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime, nullable=True)
    
    rejected_reason = Column(Text, nullable=True)
    rejection_details = Column(JSON, nullable=True)
    
    approval_notes = Column(Text, nullable=True)

    # Aliasing approved_notes to approval_notes for compatibility
    @property
    def approved_notes(self):
        return self.approval_notes

    @approved_notes.setter
    def approved_notes(self, value):
        self.approval_notes = value

    # METADATA
    city = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    citizen = relationship("User", back_populates="applications", foreign_keys=[citizen_id])
    assigned_officer = relationship("User", back_populates="assignments", foreign_keys=[assigned_to_user_id])
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    validation_errors = relationship("ValidationError", back_populates="application", cascade="all, delete-orphan")
    fraud_indicators = relationship("FraudIndicator", back_populates="application", cascade="all, delete-orphan")
    queue_assignments = relationship("QueueAssignment", back_populates="application", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_application_id", "application_id"),
        Index("idx_citizen_id", "citizen_id"),
        Index("idx_status", "status"),
        Index("idx_permit_type", "permit_type"),
        Index("idx_quality_score", "quality_score"),
        Index("idx_submitted_at", "submitted_at"),
        Index("idx_assigned_to", "assigned_to_user_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_city", "city"),
    )


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    document_type = Column(String(100), nullable=True)
    document_name = Column(String(255), nullable=True)
    document_path = Column(String(500), nullable=True)
    document_size = Column(Integer, nullable=True)
    
    is_required = Column(Boolean, default=False)
    is_present = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=False)
    validation_error = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="documents")

    __table_args__ = (
        Index("idx_doc_application_id", "application_id"),
    )
