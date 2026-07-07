"""Tests for /api/v1/auth endpoints (register & login)."""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

USER_PAYLOAD = {
    "email": "test@example.com",
    "password": "StrongPass123!",
    "first_name": "John",
    "last_name": "Doe",
}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def test_register_success(client):
    response = client.post(REGISTER_URL, json=USER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert data["is_admin"] is False
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post(REGISTER_URL, json=USER_PAYLOAD)
    response = client.post(REGISTER_URL, json=USER_PAYLOAD)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_invalid_email(client):
    response = client.post(REGISTER_URL, json={**USER_PAYLOAD, "email": "not-an-email"})
    assert response.status_code == 422


def test_register_missing_password(client):
    response = client.post(REGISTER_URL, json={"email": "a@b.com"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_success(client):
    client.post(REGISTER_URL, json=USER_PAYLOAD)
    response = client.post(
        LOGIN_URL,
        data={"username": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(REGISTER_URL, json=USER_PAYLOAD)
    response = client.post(
        LOGIN_URL,
        data={"username": USER_PAYLOAD["email"], "password": "WrongPass!"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        LOGIN_URL,
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401
