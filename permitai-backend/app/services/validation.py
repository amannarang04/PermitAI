from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
import re

from app.models.application import Application, ApplicationDocument
from app.models.validation_error import ValidationError, FraudIndicator
from app.models.configuration import Configuration
from app.constants.enums import ValidationErrorType, ValidationErrorSeverity, RiskLevel, ApplicationStatus
from app.constants.validation_rules import DEFAULT_RULES, REQUIRED_DOCUMENTS

class ValidationService:
    @staticmethod
    def get_config(db: Session, key: str) -> Any:
        """Fetch config value from DB, fallback to DEFAULT_RULES config"""
        config = db.query(Configuration).filter(Configuration.key == key).first()
        if not config:
            return DEFAULT_RULES.get(key)
        
        # Cast value based on type
        val_str = config.value
        val_type = config.value_type
        if val_type == "integer":
            return int(val_str)
        elif val_type == "float":
            return float(val_str)
        elif val_type == "boolean":
            return val_str.lower() in ("true", "1", "yes")
        return val_str

    @staticmethod
    def validate_application(db: Session, app_id: int, extracted_data: Dict[str, Any]) -> Application:
        """
        Validates application data, generates validation errors/fraud indicators, 
        and updates the Application record.
        """
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise ValueError("Application not found")

        # 1. Clear old validation errors, fraud indicators, and documents
        db.query(ValidationError).filter(ValidationError.application_id == app.id).delete()
        db.query(FraudIndicator).filter(FraudIndicator.application_id == app.id).delete()
        db.query(ApplicationDocument).filter(ApplicationDocument.application_id == app.id).delete()
        db.commit()

        # Extract nested details from JSON
        applicant_data = extracted_data.get("applicant", {}) or {}
        property_data = extracted_data.get("property", {}) or {}
        project_data = extracted_data.get("project", {}) or {}
        contractor_data = extracted_data.get("contractor", {}) or {}
        engineer_data = extracted_data.get("engineer", {}) or {}
        architect_data = extracted_data.get("architect", {}) or {}
        documents_data = extracted_data.get("documents", {}) or {}
        meta_data = extracted_data.get("extraction_metadata", {}) or {}

        # 2. Update application with extracted fields
        app.applicant_name = applicant_data.get("full_name")
        app.applicant_email = applicant_data.get("email")
        app.applicant_phone = applicant_data.get("phone")
        
        addr_app = applicant_data.get("address") or {}
        app.applicant_address_line1 = addr_app.get("line1")
        app.applicant_address_line2 = addr_app.get("line2")
        app.applicant_address_city = addr_app.get("city")
        app.applicant_address_state = addr_app.get("state")
        app.applicant_address_zip = addr_app.get("zip")
        
        app.applicant_id_type = applicant_data.get("id_type")
        app.applicant_id_number = applicant_data.get("id_number")

        addr_prop = property_data.get("address") or {}
        app.property_address_line1 = addr_prop.get("line1")
        app.property_address_line2 = addr_prop.get("line2")
        app.property_address_city = addr_prop.get("city")
        app.property_address_state = addr_prop.get("state")
        app.property_address_zip = addr_prop.get("zip")
        
        app.property_ward_number = property_data.get("ward_number") # might be missing
        size_prop = property_data.get("size") or {}
        app.property_size = size_prop.get("value")
        app.property_size_unit = size_prop.get("unit")
        app.property_current_use = property_data.get("current_use")
        app.property_proposed_use = property_data.get("proposed_use")
        app.property_ownership_type = property_data.get("ownership_type")

        app.permit_type = project_data.get("permit_type") or app.permit_type
        app.project_description = project_data.get("description")
        app.project_scope = project_data.get("scope")
        
        cost_proj = project_data.get("estimated_cost") or {}
        app.estimated_cost = cost_proj.get("value")
        app.estimated_cost_currency = cost_proj.get("currency", "INR")
        
        area_proj = project_data.get("construction_area") or {}
        app.construction_area = area_proj.get("value")
        app.construction_area_unit = area_proj.get("unit")

        # Parse project timeline dates safely
        def parse_date(date_str):
            if not date_str:
                return None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    pass
            return None

        app.project_start_date = parse_date(project_data.get("start_date"))
        app.project_end_date = parse_date(project_data.get("end_date"))

        app.contractor_name = contractor_data.get("name")
        app.contractor_license_number = contractor_data.get("license_number")
        app.contractor_phone = contractor_data.get("phone")
        app.contractor_email = contractor_data.get("email")
        app.contractor_address = contractor_data.get("address")

        app.engineer_name = engineer_data.get("name")
        app.engineer_license_number = engineer_data.get("license_number")
        app.architect_name = architect_data.get("name")
        app.architect_license_number = architect_data.get("license_number")

        app.extraction_confidence = meta_data.get("overall_confidence", 0.80)
        app.extraction_method = "claude_vision"
        app.processed_at = datetime.utcnow()

        # Set DB lists for processing quality score
        val_errors: List[ValidationError] = []
        fraud_flags: List[FraudIndicator] = []

        # 3. Required Fields Validations
        required_fields = [
            ("applicant_name", "Applicant Name", ValidationErrorSeverity.CRITICAL),
            ("applicant_email", "Applicant Email", ValidationErrorSeverity.CRITICAL),
            ("applicant_phone", "Applicant Phone", ValidationErrorSeverity.CRITICAL),
            ("applicant_address_line1", "Applicant Address", ValidationErrorSeverity.WARNING),
            ("property_address_line1", "Property Address", ValidationErrorSeverity.CRITICAL),
            ("estimated_cost", "Estimated Cost", ValidationErrorSeverity.CRITICAL),
            ("construction_area", "Construction Area", ValidationErrorSeverity.CRITICAL),
        ]

        for field_name, field_title, severity in required_fields:
            val = getattr(app, field_name)
            if val is None or val == "":
                err = ValidationError(
                    application_id=app.id,
                    field_name=field_name,
                    error_type=ValidationErrorType.MISSING_REQUIRED,
                    error_message=f"{field_title} is missing from the submitted form.",
                    error_severity=severity,
                    suggestion=f"Provide the {field_title} in the resubmission form."
                )
                val_errors.append(err)

        # 4. Format Validations (Email & Phone)
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if app.applicant_email and not re.match(email_regex, app.applicant_email):
            val_errors.append(ValidationError(
                application_id=app.id,
                field_name="applicant_email",
                error_type=ValidationErrorType.INVALID_FORMAT,
                error_message="Applicant email format is invalid.",
                error_severity=ValidationErrorSeverity.WARNING,
                suggestion="Double-check the spelling of the email address."
            ))

        phone_regex = r"^\+?1?\d{9,15}$"
        # Clean special chars from phone to validate numbers
        clean_phone = re.sub(r"[\s\-\(\)\+]", "", app.applicant_phone or "")
        if app.applicant_phone and not re.match(phone_regex, clean_phone):
            val_errors.append(ValidationError(
                application_id=app.id,
                field_name="applicant_phone",
                error_type=ValidationErrorType.INVALID_FORMAT,
                error_message="Applicant phone number format is invalid.",
                error_severity=ValidationErrorSeverity.WARNING,
                suggestion="Ensure phone number contains 10 digits and country code if necessary."
            ))

        # 5. Business Logic: Cost Thresholds
        cost_min = ValidationService.get_config(db, "validation_rule_cost_min")
        cost_max = ValidationService.get_config(db, "validation_rule_cost_max")
        
        if app.estimated_cost is not None:
            if app.estimated_cost < cost_min:
                val_errors.append(ValidationError(
                    application_id=app.id,
                    field_name="estimated_cost",
                    error_type=ValidationErrorType.BUSINESS_LOGIC,
                    error_message=f"Estimated cost is suspiciously low (less than {cost_min}).",
                    error_severity=ValidationErrorSeverity.WARNING,
                    suggestion="Verify the estimated cost or project details."
                ))
            elif app.estimated_cost > cost_max:
                val_errors.append(ValidationError(
                    application_id=app.id,
                    field_name="estimated_cost",
                    error_type=ValidationErrorType.BUSINESS_LOGIC,
                    error_message=f"Estimated cost exceeds maximum allowed value for auto-validation ({cost_max}).",
                    error_severity=ValidationErrorSeverity.CRITICAL,
                    suggestion="Route to Director review directly."
                ))

        # 6. Documents Checklist Verification
        for doc_type in REQUIRED_DOCUMENTS:
            doc_present = documents_data.get(doc_type)
            # doc_present can be boolean or string
            is_present = False
            is_valid = False
            val_err_desc = None

            if isinstance(doc_present, bool):
                is_present = doc_present
                is_valid = doc_present
            elif isinstance(doc_present, str):
                is_present = doc_present.lower() not in ("false", "missing", "absent", "none")
                is_valid = is_present

            # Create ApplicationDocument record
            db_doc = ApplicationDocument(
                application_id=app.id,
                document_type=doc_type,
                document_name=f"Extracted {doc_type.replace('_', ' ').title()}",
                is_required=True,
                is_present=is_present,
                is_valid=is_valid
            )
            
            if not is_present:
                val_err_desc = f"Required document '{doc_type}' is missing."
                db_doc.validation_error = val_err_desc
                
                # Add validation error
                val_errors.append(ValidationError(
                    application_id=app.id,
                    field_name=f"documents.{doc_type}",
                    error_type=ValidationErrorType.MISSING_REQUIRED,
                    error_message=val_err_desc,
                    error_severity=ValidationErrorSeverity.CRITICAL,
                    suggestion=f"Please upload the {doc_type.replace('_', ' ')}."
                ))
            db.add(db_doc)

        # 7. Fraud Detection Indicators
        fraud_enabled = ValidationService.get_config(db, "fraud_detection_enabled")
        if fraud_enabled:
            # Rule A: Cost Variance suspicion (Cost per unit area)
            if app.estimated_cost and app.construction_area:
                cost_per_sqft = float(app.estimated_cost) / float(app.construction_area)
                
                # Assume typical construction rate is 1500 to 4500 INR/sq ft
                # If it falls way outside this, flag it
                variance_threshold = ValidationService.get_config(db, "cost_variance_threshold")
                
                # Let's say average building cost is 2500 per sq ft.
                # If cost per sqft is < 800 or > 7000, trigger warning
                if cost_per_sqft < 800 or cost_per_sqft > 7000:
                    indicator = FraudIndicator(
                        application_id=app.id,
                        indicator_type="cost_suspicion",
                        indicator_description=f"Suspicious cost per sq ft (INR {cost_per_sqft:.2f}/sq ft). Standard range is 1500 - 4500.",
                        risk_score=0.75,
                        risk_level=RiskLevel.HIGH,
                        recommendation="investigate"
                    )
                    fraud_flags.append(indicator)

            # Rule B: Contractor Permit Volume
            if app.contractor_license_number:
                volume_threshold = ValidationService.get_config(db, "contractor_volume_threshold")
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                
                # Count applications by this contractor in last 30 days
                contractor_permits = db.query(Application).filter(
                    Application.contractor_license_number == app.contractor_license_number,
                    Application.submitted_at >= thirty_days_ago,
                    Application.id != app.id
                ).count()
                
                if contractor_permits >= volume_threshold:
                    indicator = FraudIndicator(
                        application_id=app.id,
                        indicator_type="contractor_volume",
                        indicator_description=f"Contractor has submitted {contractor_permits + 1} permit applications in the last 30 days. Threshold is {volume_threshold}.",
                        risk_score=0.60,
                        risk_level=RiskLevel.MEDIUM,
                        recommendation="investigate"
                    )
                    fraud_flags.append(indicator)

        # 8. Calculate Quality Score (0-100)
        quality_score = 100
        for err in val_errors:
            if err.error_severity == ValidationErrorSeverity.CRITICAL:
                quality_score -= 20
            elif err.error_severity == ValidationErrorSeverity.WARNING:
                quality_score -= 10
            elif err.error_severity == ValidationErrorSeverity.INFO:
                quality_score -= 2

        # Cap quality score at 0
        app.quality_score = max(0, quality_score)

        # Save all errors and indicators to DB
        for err in val_errors:
            db.add(err)
        for flag in fraud_flags:
            db.add(flag)

        # Update status based on findings
        # Flagged status if high-risk fraud or critical database mismatches
        has_critical_validation = any(err.error_severity == ValidationErrorSeverity.CRITICAL for err in val_errors)
        has_high_risk_fraud = any(flag.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) for flag in fraud_flags)
        
        if has_high_risk_fraud:
            app.status = ApplicationStatus.FLAGGED
        elif has_critical_validation:
            app.status = ApplicationStatus.PENDING_DOCS
        else:
            app.status = ApplicationStatus.PROCESSING

        db.commit()
        db.refresh(app)
        return app
