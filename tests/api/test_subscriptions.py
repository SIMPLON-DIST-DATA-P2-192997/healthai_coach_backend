"""Tests for /api/v1/subscriptions endpoints (self-service subscription tiers)."""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
SUBSCRIPTIONS_URL = "/api/v1/subscriptions"
CURRENT_URL = "/api/v1/subscriptions/current"

USER_PAYLOAD = {
    "email": "subscriber@example.com",
    "password": "StrongPass123!",
    "first_name": "Sub",
    "last_name": "Scriber",
}


def _get_token(client, payload=None):
    p = payload or USER_PAYLOAD
    client.post(REGISTER_URL, json=p)
    resp = client.post(LOGIN_URL, data={"username": p["email"], "password": p["password"]})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Registration side effect: everyone starts on a free subscription
# ---------------------------------------------------------------------------

def test_registration_creates_free_subscription(client):
    token = _get_token(client)
    response = client.get(CURRENT_URL, headers=_auth(token))
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["status"] == "active"
    assert data["price_eur_cents"] == 0
    assert data["organization_id"] is None


def test_list_my_subscriptions_unauthenticated(client):
    response = client.get(SUBSCRIPTIONS_URL)
    assert response.status_code == 401


def test_current_subscription_unauthenticated(client):
    response = client.get(CURRENT_URL)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Subscribe / change tier
# ---------------------------------------------------------------------------

def test_subscribe_to_premium_closes_free_and_opens_premium(client):
    token = _get_token(client)
    response = client.post(SUBSCRIPTIONS_URL, json={"tier": "premium"}, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["tier"] == "premium"
    assert data["status"] == "active"
    assert data["price_eur_cents"] == 999

    history = client.get(SUBSCRIPTIONS_URL, headers=_auth(token)).json()
    assert len(history) == 2
    statuses = {h["tier"]: h["status"] for h in history}
    assert statuses["free"] == "cancelled"
    assert statuses["premium"] == "active"


def test_subscribe_to_premium_plus_price(client):
    token = _get_token(client)
    response = client.post(SUBSCRIPTIONS_URL, json={"tier": "premium_plus"}, headers=_auth(token))
    assert response.status_code == 201
    assert response.json()["price_eur_cents"] == 1999


def test_subscribe_only_one_active_at_a_time(client):
    token = _get_token(client)
    client.post(SUBSCRIPTIONS_URL, json={"tier": "premium"}, headers=_auth(token))
    client.post(SUBSCRIPTIONS_URL, json={"tier": "premium_plus"}, headers=_auth(token))

    current = client.get(CURRENT_URL, headers=_auth(token)).json()
    assert current["tier"] == "premium_plus"

    history = client.get(SUBSCRIPTIONS_URL, headers=_auth(token)).json()
    active = [h for h in history if h["status"] == "active"]
    assert len(active) == 1


def test_subscribe_b2b_not_allowed_self_service(client):
    token = _get_token(client)
    response = client.post(SUBSCRIPTIONS_URL, json={"tier": "b2b"}, headers=_auth(token))
    assert response.status_code == 422


def test_subscribe_invalid_tier(client):
    token = _get_token(client)
    response = client.post(SUBSCRIPTIONS_URL, json={"tier": "gold"}, headers=_auth(token))
    assert response.status_code == 422


def test_subscribe_unauthenticated(client):
    response = client.post(SUBSCRIPTIONS_URL, json={"tier": "premium"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------

def test_cancel_falls_back_to_free(client):
    token = _get_token(client)
    client.post(SUBSCRIPTIONS_URL, json={"tier": "premium"}, headers=_auth(token))

    response = client.delete(CURRENT_URL, headers=_auth(token))
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["status"] == "active"


def test_cancel_while_already_free_is_a_noop(client):
    token = _get_token(client)
    response = client.delete(CURRENT_URL, headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["tier"] == "free"

    history = client.get(SUBSCRIPTIONS_URL, headers=_auth(token)).json()
    assert len(history) == 1


def test_cancel_unauthenticated(client):
    response = client.delete(CURRENT_URL)
    assert response.status_code == 401
