from app.api.auth import router as auth_router
from app.api.applications import router as applications_router
from app.api.queues import router as queues_router
from app.api.metrics import router as metrics_router
from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.api.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "applications_router",
    "queues_router",
    "metrics_router",
    "admin_router",
    "health_router",
    "notifications_router"
]

