from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from app.config import settings
from app.api import (
    auth_router,
    applications_router,
    queues_router,
    metrics_router,
    admin_router,
    health_router,
    notifications_router
)
from app.middleware import ErrorHandlingMiddleware, LoggingMiddleware
from app.database.db import Base, engine
from app.database.session import SessionLocal
from app.models.configuration import Configuration
from app.models.user import User
from app.services.auth import AuthService

# Create DB tables if they do not exist (SQLite auto-creation)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PermitAI API",
    description="Automated Building Permit Processing & Compliance Review Platform",
    version="1.0.0"
)

# Configure CORS Origins
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    try:
        origins = json.loads(origins)
    except Exception:
        origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# API Routes
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(queues_router)
app.include_router(metrics_router)
app.include_router(admin_router)
app.include_router(notifications_router)

@app.on_event("startup")
def seed_database():
    """
    On startup, populate defaults for configuration rules and create test accounts
    if the database is fresh.
    """
    db = SessionLocal()
    try:
        # Seed configurations
        configs_to_seed = [
            ('validation_rule_cost_min', '10000', 'integer', 'Minimum estimated cost for permit'),
            ('validation_rule_cost_max', '10000000', 'integer', 'Maximum estimated cost for permit'),
            ('auto_approval_threshold', '500000', 'integer', 'Cost threshold for auto-approval in INR (5 Lakhs)'),
            ('fraud_detection_enabled', 'true', 'boolean', 'Enable fraud detection'),
            ('email_notifications_enabled', 'true', 'boolean', 'Enable email notifications'),
            ('quality_score_threshold_good', '90', 'integer', 'Quality score threshold for good quality'),
            ('quality_score_threshold_acceptable', '70', 'integer', 'Quality score threshold for acceptable quality'),
            ('extraction_confidence_threshold', '0.85', 'float', 'Claude extraction confidence threshold'),
            ('max_file_size_mb', '10', 'integer', 'Maximum file upload size in MB'),
            ('contractor_volume_threshold', '5', 'integer', 'Max permits per contractor per month'),
            ('cost_variance_threshold', '0.2', 'float', 'Cost variance from market average (20%)')
        ]
        for key, val, val_type, desc in configs_to_seed:
            exists = db.query(Configuration).filter(Configuration.key == key).first()
            if not exists:
                db.add(Configuration(
                    key=key,
                    value=val,
                    value_type=val_type,
                    description=desc
                ))
        db.commit()

        # Seed test user accounts (hashed password matches username + 'password')
        users_to_seed = [
            ("admin", "admin@permitai.com", "adminpassword", "System Administrator", "admin", None),
            ("officer", "officer@permitai.com", "officerpassword", "Review Officer (Building)", "officer", "Building"),
            ("electrical_officer", "electrical@permitai.com", "officerpassword", "Review Officer (Electrical)", "officer", "Electrical"),
            ("plumbing_officer", "plumbing@permitai.com", "officerpassword", "Review Officer (Plumbing)", "officer", "Plumbing"),
            ("supervisor", "supervisor@permitai.com", "supervisorpassword", "Supervisor", "supervisor", None),
            ("director", "director@permitai.com", "directorpassword", "Director", "director", None),
            ("citizen", "citizen@permitai.com", "citizenpassword", "Rajesh Kumar (Citizen)", "citizen", None)
        ]
        for username, email, pwd, name, role, dept in users_to_seed:
            exists = db.query(User).filter(User.username == username).first()
            if not exists:
                db.add(User(
                    username=username,
                    email=email,
                    password_hash=AuthService.hash_password(pwd),
                    full_name=name,
                    role=role,
                    department=dept,
                    is_active=True
                ))
        db.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()
