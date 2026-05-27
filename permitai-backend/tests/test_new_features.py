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

def test_officer_rejection_and_docs_endpoints(client, db):
    # 1. Setup mock application
    # Register and login citizen
    client.post("/api/auth/register", json={
        "username": "workflowcitizen",
        "email": "workflowcitizen@example.com",
        "password": "testpassword",
        "full_name": "Workflow Citizen"
    })
    
    res_login = client.post("/api/auth/login", data={
        "username": "workflowcitizen",
        "password": "testpassword"
    })
    citizen_token = res_login.json()["access_token"]
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    
    citizen_user = db.query(User).filter(User.username == "workflowcitizen").first()
    
    app_record = Application(
        application_id="PRM-2026-WORKFLOW",
        citizen_id=citizen_user.id,
        status=ApplicationStatus.UNDER_REVIEW,
        permit_type="Building",
        estimated_cost=1500000.0,
        construction_area=500.0,
        applicant_name="Workflow Citizen",
        applicant_email="workflowcitizen@example.com"
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)

    # 2. Setup officer and login
    officer = User(
        username="workflowofficer",
        email="workflowofficer@example.com",
        password_hash=AuthService.hash_password("officerpassword"),
        role=UserRole.OFFICER,
        is_active=True
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)

    # Setup queue assignment
    assignment = QueueAssignment(
        application_id=app_record.id,
        queue_name="building_engineer_review",
        assigned_to_user_id=officer.id,
        status=QueueAssignmentStatus.PENDING
    )
    db.add(assignment)
    db.commit()

    # Debug print
    all_assignments = db.query(QueueAssignment).all()
    print("ALL ASSIGNMENTS IN TEST:", all_assignments)
    for a in all_assignments:
        print(f"a.id={a.id}, a.assigned_to_user_id={a.assigned_to_user_id}, a.status={a.status}")

    res_login_off = client.post("/api/auth/login", data={
        "username": "workflowofficer",
        "password": "officerpassword"
    })
    officer_token = res_login_off.json()["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # 3. Test queue /my-queue endpoint
    res_my_queue = client.get("/api/queues/my-queue", headers=officer_headers)
    assert res_my_queue.status_code == 200
    assert len(res_my_queue.json()) == 1
    assert res_my_queue.json()[0]["queue_name"] == "building_engineer_review"

    # 4. Test queues /details endpoint
    res_details = client.get(f"/api/queues/{app_record.application_id}/details", headers=officer_headers)
    assert res_details.status_code == 200
    assert res_details.json()["application_id"] == app_record.application_id

    # 5. Test request missing documents
    res_req_docs = client.post(
        f"/api/applications/{app_record.application_id}/request-documents",
        json={"missing_documents": ["site_plan", "structural_drawings"], "deadline_days": 14},
        headers=officer_headers
    )
    assert res_req_docs.status_code == 200
    assert res_req_docs.json()["status"] == "pending_docs"
    
    # Verify in DB
    db.refresh(app_record)
    assert app_record.status == ApplicationStatus.PENDING_DOCS
    assert app_record.rejection_details["missing_documents"] == ["site_plan", "structural_drawings"]
    assert app_record.rejection_details["deadline_days"] == 14

    # 6. Test reject endpoint
    # Reset status first
    app_record.status = ApplicationStatus.UNDER_REVIEW
    db.commit()
    
    res_reject = client.post(
        f"/api/applications/{app_record.application_id}/reject",
        json={"reason": "Estimates too low", "required_changes": ["Raise construction area details"]},
        headers=officer_headers
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "rejected"
    
    db.refresh(app_record)
    assert app_record.status == ApplicationStatus.REJECTED
    assert app_record.rejected_reason == "Estimates too low"
    assert app_record.rejection_details["required_changes"] == ["Raise construction area details"]

