"""Tests for /api/v1/users endpoints (current user profile)."""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/users/me"

USER_PAYLOAD = {
    "email": "user@example.com",
    "password": "StrongPass123!",
    "first_name": "Jane",
    "last_name": "Smith",
}


def _get_token(client, payload=None):
    """Helper: register + login, return Bearer token."""
    p = payload or USER_PAYLOAD
    client.post(REGISTER_URL, json=p)
    resp = client.post(LOGIN_URL, data={"username": p["email"], "password": p["password"]})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------

def test_get_me(client):
    token = _get_token(client)
    response = client.get(ME_URL, headers=_auth(token))
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert data["is_admin"] is False


def test_get_me_unauthenticated(client):
    response = client.get(ME_URL)
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    response = client.get(ME_URL, headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PUT /users/me
# ---------------------------------------------------------------------------

def test_update_me(client):
    token = _get_token(client)
    response = client.put(
        ME_URL,
        json={"first_name": "Updated", "last_name": "Name"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    assert data["email"] == USER_PAYLOAD["email"]


def test_update_me_unauthenticated(client):
    response = client.put(ME_URL, json={"first_name": "X"})
    assert response.status_code == 401
