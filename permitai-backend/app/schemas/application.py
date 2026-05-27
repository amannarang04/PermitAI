from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Sub-schemas for nested detailed response
class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

class ValueWithUnit(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None

class CostInfo(BaseModel):
    value: Optional[float] = None
    currency: Optional[str] = "INR"

class ApplicantInfo(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None

class PropertyInfo(BaseModel):
    address: Optional[Address] = None
    size: Optional[ValueWithUnit] = None
    current_use: Optional[str] = None
    proposed_use: Optional[str] = None
    ownership_type: Optional[str] = None

class ProjectInfo(BaseModel):
    permit_type: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    estimated_cost: Optional[CostInfo] = None
    construction_area: Optional[ValueWithUnit] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ContractorInfo(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class EngineerInfo(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None

class ArchitectInfo(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None

# Base response schemas
class DocumentResponse(BaseModel):
    id: int
    document_type: str
    document_name: str
    document_path: Optional[str] = None
    document_size: Optional[int] = None
    is_required: bool
    is_present: bool
    is_valid: bool
    validation_error: Optional[str] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ValidationErrorSchema(BaseModel):
    id: int
    field_name: Optional[str]
    error_type: str
    error_message: Optional[str]
    error_severity: str
    suggestion: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FraudIndicatorSchema(BaseModel):
    id: int
    indicator_type: Optional[str]
    indicator_description: Optional[str]
    risk_score: Optional[float]
    risk_level: str
    recommendation: Optional[str]
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QueueHistorySchema(BaseModel):
    id: int
    from_queue: Optional[str]
    to_queue: Optional[str]
    moved_by_user_id: Optional[int]
    moved_at: datetime
    reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ApplicationResponse(BaseModel):
    id: int
    application_id: str
    citizen_id: int
    status: str
    quality_score: Optional[int]
    extraction_confidence: Optional[float]
    applicant_name: Optional[str]
    permit_type: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApplicationListResponse(BaseModel):
    total: int
    applications: List[ApplicationResponse]

class ApplicationDetailResponse(BaseModel):
    id: int
    application_id: str
    status: str
    quality_score: Optional[int]
    extraction_confidence: Optional[float]
    submitted_at: datetime
    processed_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    decided_at: Optional[datetime]
    assigned_to_user_id: Optional[int]
    assigned_at: Optional[datetime]
    original_file_name: Optional[str]
    original_file_path: Optional[str]
    original_file_size: Optional[int]
    original_file_type: Optional[str]
    extracted_text: Optional[str]
    approval_notes: Optional[str]
    rejected_reason: Optional[str]
    city: Optional[str]

    # Nested structures mapped in the validator
    applicant: ApplicantInfo
    property: PropertyInfo
    project: ProjectInfo
    contractor: ContractorInfo
    engineer: EngineerInfo
    architect: ArchitectInfo

    # Relationships
    documents: List[DocumentResponse]
    red_flags: List[FraudIndicatorSchema]
    validation_errors: List[ValidationErrorSchema]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def nest_flat_fields(cls, data):
        # If it is a DB model instance or a dict
        is_obj = not isinstance(data, dict)
        
        def get_val(key, default=None):
            return getattr(data, key, default) if is_obj else data.get(key, default)

        # Build nested structs
        applicant = ApplicantInfo(
            full_name=get_val("applicant_name"),
            email=get_val("applicant_email"),
            phone=get_val("applicant_phone"),
            address=Address(
                line1=get_val("applicant_address_line1"),
                line2=get_val("applicant_address_line2"),
                city=get_val("applicant_address_city"),
                state=get_val("applicant_address_state"),
                zip=get_val("applicant_address_zip")
            ),
            id_type=get_val("applicant_id_type"),
            id_number=get_val("applicant_id_number")
        )

        property_info = PropertyInfo(
            address=Address(
                line1=get_val("property_address_line1"),
                line2=get_val("property_address_line2"),
                city=get_val("property_address_city"),
                state=get_val("property_address_state"),
                zip=get_val("property_address_zip")
            ),
            size=ValueWithUnit(
                value=float(get_val("property_size")) if get_val("property_size") is not None else None,
                unit=get_val("property_size_unit")
            ),
            current_use=get_val("property_current_use"),
            proposed_use=get_val("property_proposed_use"),
            ownership_type=get_val("property_ownership_type")
        )

        project = ProjectInfo(
            permit_type=get_val("permit_type"),
            description=get_val("project_description"),
            scope=get_val("project_scope"),
            estimated_cost=CostInfo(
                value=float(get_val("estimated_cost")) if get_val("estimated_cost") is not None else None,
                currency=get_val("estimated_cost_currency", "INR")
            ),
            construction_area=ValueWithUnit(
                value=float(get_val("construction_area")) if get_val("construction_area") is not None else None,
                unit=get_val("construction_area_unit")
            ),
            start_date=get_val("project_start_date"),
            end_date=get_val("project_end_date")
        )

        contractor = ContractorInfo(
            name=get_val("contractor_name"),
            license_number=get_val("contractor_license_number"),
            phone=get_val("contractor_phone"),
            email=get_val("contractor_email"),
            address=get_val("contractor_address")
        )

        engineer = EngineerInfo(
            name=get_val("engineer_name"),
            license_number=get_val("engineer_license_number")
        )

        architect = ArchitectInfo(
            name=get_val("architect_name"),
            license_number=get_val("architect_license_number")
        )

        # Fetch fraud indicators from relationship and rename to red_flags
        fraud_inds = get_val("fraud_indicators", [])
        
        # Prepare result dict
        res = {}
        if is_obj:
            # Copy all fields from ORM object attributes
            for field in cls.model_fields:
                if field not in ["applicant", "property", "project", "contractor", "engineer", "architect", "red_flags", "documents", "validation_errors"]:
                    res[field] = getattr(data, field, None)
            res["documents"] = getattr(data, "documents", [])
            res["validation_errors"] = getattr(data, "validation_errors", [])
        else:
            res = data.copy()

        res["applicant"] = applicant
        res["property"] = property_info
        res["project"] = project
        res["contractor"] = contractor
        res["engineer"] = engineer
        res["architect"] = architect
        res["red_flags"] = fraud_inds

        return res
