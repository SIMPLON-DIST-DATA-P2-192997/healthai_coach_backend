"""Tests for /api/v1/admin endpoints (admin-only user management)."""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ADMIN_USERS_URL = "/api/v1/admin/users"

ADMIN_PAYLOAD = {
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "first_name": "Admin",
    "last_name": "User",
}

REGULAR_PAYLOAD = {
    "email": "regular@example.com",
    "password": "UserPass123!",
    "first_name": "Regular",
    "last_name": "User",
}


def _register_and_login(client, payload):
    client.post(REGISTER_URL, json=payload)
    resp = client.post(LOGIN_URL, data={"username": payload["email"], "password": payload["password"]})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _make_admin(db_session, email):
    """Directly set is_admin=True in DB for a user."""
    from api.models.user import User
    user = db_session.query(User).filter(User.email == email).first()
    user.is_admin = True
    db_session.commit()


# ---------------------------------------------------------------------------
# GET /admin/users
# ---------------------------------------------------------------------------

def test_list_users_as_admin(client, db_session):
    _register_and_login(client, REGULAR_PAYLOAD)
    _register_and_login(client, ADMIN_PAYLOAD)
    _make_admin(db_session, ADMIN_PAYLOAD["email"])
    token = client.post(LOGIN_URL, data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}).json()["access_token"]

    response = client.get(ADMIN_USERS_URL, headers=_auth(token))
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert REGULAR_PAYLOAD["email"] in emails
    assert ADMIN_PAYLOAD["email"] in emails


def test_list_users_as_regular_user(client):
    token = _register_and_login(client, REGULAR_PAYLOAD)
    response = client.get(ADMIN_USERS_URL, headers=_auth(token))
    assert response.status_code == 403


def test_list_users_unauthenticated(client):
    response = client.get(ADMIN_USERS_URL)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /admin/users/{user_id}
# ---------------------------------------------------------------------------

def test_get_user_as_admin(client, db_session):
    _register_and_login(client, REGULAR_PAYLOAD)
    _register_and_login(client, ADMIN_PAYLOAD)
    _make_admin(db_session, ADMIN_PAYLOAD["email"])
    token = client.post(LOGIN_URL, data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}).json()["access_token"]

    from api.models.user import User
    user = db_session.query(User).filter(User.email == REGULAR_PAYLOAD["email"]).first()
    response = client.get(f"{ADMIN_USERS_URL}/{user.id}", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["email"] == REGULAR_PAYLOAD["email"]


def test_get_user_not_found(client, db_session):
    _register_and_login(client, ADMIN_PAYLOAD)
    _make_admin(db_session, ADMIN_PAYLOAD["email"])
    token = client.post(LOGIN_URL, data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}).json()["access_token"]

    response = client.get(f"{ADMIN_USERS_URL}/99999", headers=_auth(token))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /admin/users/{user_id}
# ---------------------------------------------------------------------------

def test_delete_user_as_admin(client, db_session):
    _register_and_login(client, REGULAR_PAYLOAD)
    _register_and_login(client, ADMIN_PAYLOAD)
    _make_admin(db_session, ADMIN_PAYLOAD["email"])
    token = client.post(LOGIN_URL, data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}).json()["access_token"]

    from api.models.user import User
    user = db_session.query(User).filter(User.email == REGULAR_PAYLOAD["email"]).first()
    response = client.delete(f"{ADMIN_USERS_URL}/{user.id}", headers=_auth(token))
    assert response.status_code == 204


def test_delete_user_as_regular_user(client):
    token = _register_and_login(client, REGULAR_PAYLOAD)
    response = client.delete(f"{ADMIN_USERS_URL}/1", headers=_auth(token))
    assert response.status_code == 403
