# Default validation rules and thresholds (fallback settings)

DEFAULT_RULES = {
    "validation_rule_cost_min": 10000,
    "validation_rule_cost_max": 10000000,
    "auto_approval_threshold": 500000,  # 5 Lakhs (500,000 INR)
    "fraud_detection_enabled": True,
    "email_notifications_enabled": True,
    "quality_score_threshold_good": 90,
    "quality_score_threshold_acceptable": 70,
    "extraction_confidence_threshold": 0.85,
    "max_file_size_mb": 10,
    "contractor_volume_threshold": 5,
    "cost_variance_threshold": 0.20,  # 20%
}

# The documents that must be present and valid
REQUIRED_DOCUMENTS = [
    "site_plan",
    "drawings",
    "property_deed",
    "id_proof"
]
