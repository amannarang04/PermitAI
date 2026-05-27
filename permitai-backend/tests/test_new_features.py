import pytest
from app.models.user import User
from app.models.application import Application
from app.models.notification import InAppNotification
from app.models.queue_assignment import QueueAssignment
from app.constants.enums import ApplicationStatus, QueueAssignmentStatus, UserRole
from app.services.auth import AuthService
from datetime import datetime

def test_notifications_and_preferences(client, db):
    # 1. Register and login citizen
    client.post("/api/auth/register", json={
        "username": "notifcitizen",
        "email": "notifcitizen@example.com",
        "password": "testpassword",
        "full_name": "Notif Citizen"
    })
    
    res_login = client.post("/api/auth/login", data={
        "username": "notifcitizen",
        "password": "testpassword"
    })
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial notifications (empty)
    res_notif = client.get("/api/notifications", headers=headers)
    assert res_notif.status_code == 200
    assert len(res_notif.json()) == 0

    # 3. Create a test notification in DB manually
    user = db.query(User).filter(User.username == "notifcitizen").first()
    notification = InAppNotification(
        user_id=user.id,
        title="Test Notification",
        message="This is a test notification message",
        notification_type="received"
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # 4. Fetch notifications and verify
    res_notif = client.get("/api/notifications", headers=headers)
    assert res_notif.status_code == 200
    assert len(res_notif.json()) == 1
    notif_data = res_notif.json()[0]
    assert notif_data["title"] == "Test Notification"
    assert notif_data["is_read"] is False

    # 5. Mark as read
    notif_id = notif_data["id"]
    res_read = client.patch(f"/api/notifications/{notif_id}/read", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["is_read"] is True

    # 6. Update notification preferences
    res_pref = client.patch("/api/notifications/preferences", json={
        "email": False,
        "sms": True,
        "in_app": False
    }, headers=headers)
    assert res_pref.status_code == 200
    
    db.refresh(user)
    assert user.notification_preferences == {"email": False, "sms": True, "in_app": False}


def test_download_permit_endpoint(client, db):
    # 1. Setup mock application with APPROVED status and permit_number
    # Register and login citizen
    client.post("/api/auth/register", json={
        "username": "permitcitizen",
        "email": "permitcitizen@example.com",
        "password": "testpassword",
        "full_name": "Permit Citizen"
    })
    
    res_login = client.post("/api/auth/login", data={
        "username": "permitcitizen",
        "password": "testpassword"
    })
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    user = db.query(User).filter(User.username == "permitcitizen").first()
    
    app_record = Application(
        application_id="PRM-2026-TESTPERMIT",
        citizen_id=user.id,
        status=ApplicationStatus.APPROVED,
        permit_type="Building",
        permit_number="BP-2026-TESTPERMIT",
        estimated_cost=1500000.0,
        construction_area=500.0,
        applicant_name="Permit Citizen",
        applicant_email="permitcitizen@example.com"
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)

    # 2. Try to download as authorized citizen
    res_download = client.get(f"/api/applications/{app_record.application_id}/download-permit", headers=headers)
    assert res_download.status_code == 200
    assert res_download.headers["content-type"] == "application/pdf"
    assert len(res_download.content) > 0


def test_metrics_endpoints(client, db):
    # 1. Setup supervisor account manually
    supervisor = User(
        username="testsupervisor",
        email="testsupervisor@example.com",
        password_hash=AuthService.hash_password("supervisorpassword"),
        role=UserRole.SUPERVISOR,
        is_active=True
    )
    db.add(supervisor)
    db.commit()
    db.refresh(supervisor)

    # Login as supervisor
    res_login = client.post("/api/auth/login", data={
        "username": "testsupervisor",
        "password": "supervisorpassword"
    })
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test get detailed queue status
    res_qs = client.get("/api/admin/metrics/queue-status", headers=headers)
    assert res_qs.status_code == 200
    assert len(res_qs.json()) > 0
    assert "queue_name" in res_qs.json()[0]

    # 3. Test officer productivity
    res_op = client.get("/api/admin/metrics/officer-productivity", headers=headers)
    assert res_op.status_code == 200
    assert len(res_op.json()) > 0

    # 4. Test bottleneck analysis
    res_ba = client.get("/api/admin/metrics/bottleneck-analysis", headers=headers)
    assert res_ba.status_code == 200
    assert len(res_ba.json()) > 0

    # 5. Test trends
    res_tr = client.get("/api/admin/metrics/trends?days=7", headers=headers)
    assert res_tr.status_code == 200
    assert "trends" in res_tr.json()
