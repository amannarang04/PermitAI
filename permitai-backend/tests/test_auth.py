from app.models.user import User

def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_and_login(client, db):
    # 1. Register a test citizen
    res = client.post("/api/auth/register", json={
        "username": "testcitizen",
        "email": "testcitizen@example.com",
        "password": "testpassword",
        "full_name": "Test Citizen User",
        "phone": "+91-1234567890"
    })
    assert res.status_code == 200
    assert res.json()["username"] == "testcitizen"
    assert res.json()["role"] == "citizen"
    
    # 2. Prevent duplicate registrations
    res_dup = client.post("/api/auth/register", json={
        "username": "testcitizen",
        "email": "testcitizen2@example.com",
        "password": "differentpassword"
    })
    assert res_dup.status_code == 400

    # 3. Authenticate and retrieve token
    res_login = client.post("/api/auth/login", data={
        "username": "testcitizen",
        "password": "testpassword"
    })
    assert res_login.status_code == 200
    data = res_login.json()
    assert "access_token" in data
    assert data["role"] == "citizen"

    # 4. Access secure endpoint using auth token
    token = data["access_token"]
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "testcitizen"
