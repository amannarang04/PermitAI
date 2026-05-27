import pytest
from app.models.application import Application
from app.models.user import User
from app.constants.enums import ApplicationStatus

def test_upload_and_process_application(client, db):
    # 1. Citizen Login
    res_login = client.post("/api/auth/login", data={
        "username": "citizen",
        "password": "citizenpassword"
    })
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload building permit form PDF
    file_content = b"%PDF-1.4 dummy pdf content for building permit"
    files = {"file": ("Hebbal_building_permit.pdf", file_content, "application/pdf")}
    
    res_upload = client.post("/api/applications/upload", files=files, headers=headers)
    assert res_upload.status_code == 200
    upload_data = res_upload.json()
    assert "application_id" in upload_data
    app_id_str = upload_data["application_id"]

    # 3. Track the application status
    res_track = client.get(f"/api/applications/track/{app_id_str}", headers=headers)
    assert res_track.status_code == 200
    track_data = res_track.json()
    assert track_data["application_id"] == app_id_str
    # Verify status is UNDER_REVIEW or PROCESSING or FLAGGED
    assert track_data["status"] in ("under_review", "processing", "flagged")
    assert track_data["quality_score"] is not None

    # Verify DB values directly
    app_record = db.query(Application).filter(Application.application_id == app_id_str).first()
    assert app_record is not None
    assert app_record.applicant_name == "Rajesh Kumar"
    assert app_record.estimated_cost == 1500000.0
    assert len(app_record.validation_errors) == 0  # Hebrew_permit template has all docs

    # 4. Review Officer Login
    res_login_off = client.post("/api/auth/login", data={
        "username": "officer",
        "password": "officerpassword"
    })
    assert res_login_off.status_code == 200
    off_token = res_login_off.json()["access_token"]
    off_headers = {"Authorization": f"Bearer {off_token}"}

    # Check staff queue
    res_queue = client.get("/api/applications/queue/my-queue", headers=off_headers)
    assert res_queue.status_code == 200
    queue_data = res_queue.json()
    assert queue_data["total"] >= 1
    assert any(a["application_id"] == app_id_str for a in queue_data["applications"])

    # View details
    res_details = client.get(f"/api/applications/{app_id_str}/details", headers=off_headers)
    assert res_details.status_code == 200
    details_data = res_details.json()
    assert details_data["applicant"]["full_name"] == "Rajesh Kumar"
    assert details_data["project"]["estimated_cost"]["value"] == 1500000.0

    # Approve
    res_approve = client.post(
        f"/api/applications/{app_id_str}/approve", 
        json={"notes": "Approved Hebbal residential project", "conditions": ["Inspect site monthly"]},
        headers=off_headers
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "approved"
    assert "permit_number" in res_approve.json()
