"""Tests for /api/v1/organizations endpoints (admin-only B2B management)."""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ORGANIZATIONS_URL = "/api/v1/organizations"
CURRENT_URL = "/api/v1/subscriptions/current"

ADMIN_PAYLOAD = {
    "email": "org-admin@example.com",
    "password": "AdminPass123!",
    "first_name": "Admin",
    "last_name": "User",
}

MEMBER_PAYLOAD = {
    "email": "member@example.com",
    "password": "MemberPass123!",
    "first_name": "Member",
    "last_name": "User",
}

ORG_PAYLOAD = {"name": "Gymlife", "contact_email": "contact@gymlife.example"}


def _register_and_login(client, payload):
    client.post(REGISTER_URL, json=payload)
    resp = client.post(LOGIN_URL, data={"username": payload["email"], "password": payload["password"]})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _make_admin(db_session, email):
    from api.models.user import User
    user = db_session.query(User).filter(User.email == email).first()
    user.is_admin = True
    db_session.commit()


def _admin_token(client, db_session):
    _register_and_login(client, ADMIN_PAYLOAD)
    _make_admin(db_session, ADMIN_PAYLOAD["email"])
    return client.post(
        LOGIN_URL, data={"username": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"]}
    ).json()["access_token"]


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def test_create_and_list_organizations_as_admin(client, db_session):
    token = _admin_token(client, db_session)
    response = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(token))
    assert response.status_code == 201
    org = response.json()
    assert org["name"] == ORG_PAYLOAD["name"]

    listed = client.get(ORGANIZATIONS_URL, headers=_auth(token)).json()
    assert any(o["id"] == org["id"] for o in listed)


def test_create_organization_as_regular_user_forbidden(client):
    token = _register_and_login(client, MEMBER_PAYLOAD)
    response = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(token))
    assert response.status_code == 403


def test_create_organization_unauthenticated(client):
    response = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD)
    assert response.status_code == 401


def test_get_organization_not_found(client, db_session):
    token = _admin_token(client, db_session)
    response = client.get(f"{ORGANIZATIONS_URL}/99999", headers=_auth(token))
    assert response.status_code == 404


def test_update_organization_as_admin(client, db_session):
    token = _admin_token(client, db_session)
    org = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(token)).json()

    response = client.put(
        f"{ORGANIZATIONS_URL}/{org['id']}", json={"name": "Gymlife Updated"}, headers=_auth(token)
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Gymlife Updated"


# ---------------------------------------------------------------------------
# B2B subscription provisioning
# ---------------------------------------------------------------------------

def test_provision_b2b_subscription_for_member(client, db_session):
    admin_token = _admin_token(client, db_session)
    member_token = _register_and_login(client, MEMBER_PAYLOAD)

    from api.models.user import User
    member = db_session.query(User).filter(User.email == MEMBER_PAYLOAD["email"]).first()

    org = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(admin_token)).json()

    response = client.post(
        f"{ORGANIZATIONS_URL}/{org['id']}/subscriptions",
        json={"user_id": member.id, "price_eur_cents": 500},
        headers=_auth(admin_token),
    )
    assert response.status_code == 201
    sub = response.json()
    assert sub["tier"] == "b2b"
    assert sub["organization_id"] == org["id"]
    assert sub["price_eur_cents"] == 500

    current = client.get(CURRENT_URL, headers=_auth(member_token)).json()
    assert current["tier"] == "b2b"
    assert current["organization_id"] == org["id"]


def test_provision_b2b_subscription_unknown_user(client, db_session):
    admin_token = _admin_token(client, db_session)
    org = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(admin_token)).json()

    response = client.post(
        f"{ORGANIZATIONS_URL}/{org['id']}/subscriptions",
        json={"user_id": 99999},
        headers=_auth(admin_token),
    )
    assert response.status_code == 404


def test_provision_b2b_subscription_unknown_organization(client, db_session):
    admin_token = _admin_token(client, db_session)
    member_token = _register_and_login(client, MEMBER_PAYLOAD)

    from api.models.user import User
    member = db_session.query(User).filter(User.email == MEMBER_PAYLOAD["email"]).first()

    response = client.post(
        f"{ORGANIZATIONS_URL}/99999/subscriptions",
        json={"user_id": member.id},
        headers=_auth(admin_token),
    )
    assert response.status_code == 404


def test_provision_b2b_subscription_as_regular_user_forbidden(client, db_session):
    admin_token = _admin_token(client, db_session)
    member_token = _register_and_login(client, MEMBER_PAYLOAD)
    org = client.post(ORGANIZATIONS_URL, json=ORG_PAYLOAD, headers=_auth(admin_token)).json()

    response = client.post(
        f"{ORGANIZATIONS_URL}/{org['id']}/subscriptions",
        json={"user_id": 1},
        headers=_auth(member_token),
    )
    assert response.status_code == 403
