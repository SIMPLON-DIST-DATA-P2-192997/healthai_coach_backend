"""Tests for /api/v1/ai endpoints (AI-generated content, premium-gated).

The AI microservice isn't deployed yet, so these endpoints are backed by the
stub in api/services/ai_client.py — these tests assert the wiring (auth,
tier gating, persistence) rather than the content of the placeholder output.
"""

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
SUBSCRIPTIONS_URL = "/api/v1/subscriptions"
DIET_RECOMMENDATIONS_URL = "/api/v1/ai/diet-recommendations"
WORKOUT_PLANS_URL = "/api/v1/ai/workout-plans"
NUTRITION_PLANS_URL = "/api/v1/ai/nutrition-plans"

USER_PAYLOAD = {
    "email": "ai-user@example.com",
    "password": "StrongPass123!",
    "first_name": "AI",
    "last_name": "User",
}


def _get_token(client, payload=None):
    p = payload or USER_PAYLOAD
    client.post(REGISTER_URL, json=p)
    resp = client.post(LOGIN_URL, data={"username": p["email"], "password": p["password"]})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _upgrade_to_premium(client, token):
    client.post(SUBSCRIPTIONS_URL, json={"tier": "premium"}, headers=_auth(token))


# ---------------------------------------------------------------------------
# Tier gating — everyone starts on free (cf. test_subscriptions.py)
# ---------------------------------------------------------------------------

def test_generate_diet_recommendation_forbidden_on_free_tier(client):
    token = _get_token(client)
    response = client.post(DIET_RECOMMENDATIONS_URL, json={}, headers=_auth(token))
    assert response.status_code == 403


def test_generate_workout_plan_forbidden_on_free_tier(client):
    token = _get_token(client)
    response = client.post(WORKOUT_PLANS_URL, json={}, headers=_auth(token))
    assert response.status_code == 403


def test_generate_nutrition_plan_forbidden_on_free_tier(client):
    token = _get_token(client)
    response = client.post(NUTRITION_PLANS_URL, json={}, headers=_auth(token))
    assert response.status_code == 403


def test_list_workout_plans_forbidden_on_free_tier(client):
    token = _get_token(client)
    response = client.get(WORKOUT_PLANS_URL, headers=_auth(token))
    assert response.status_code == 403


def test_ai_endpoints_unauthenticated(client):
    assert client.post(DIET_RECOMMENDATIONS_URL, json={}).status_code == 401
    assert client.post(WORKOUT_PLANS_URL, json={}).status_code == 401
    assert client.post(NUTRITION_PLANS_URL, json={}).status_code == 401


# ---------------------------------------------------------------------------
# Diet recommendations
# ---------------------------------------------------------------------------

def test_generate_diet_recommendation_as_premium(client):
    token = _get_token(client)
    _upgrade_to_premium(client, token)

    response = client.post(DIET_RECOMMENDATIONS_URL, json={"goal": "lose weight"}, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["recommendation"] is not None
    assert data["daily_caloric_intake_kcal"] is not None
    assert "recommended_at" in data


# ---------------------------------------------------------------------------
# Workout plans
# ---------------------------------------------------------------------------

def test_generate_and_list_workout_plan_as_premium(client):
    token = _get_token(client)
    _upgrade_to_premium(client, token)

    response = client.post(WORKOUT_PLANS_URL, json={"goal": "build muscle"}, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["goal"] == "build muscle"
    assert data["plan_text"]

    history = client.get(WORKOUT_PLANS_URL, headers=_auth(token)).json()
    assert len(history) == 1
    assert history[0]["goal"] == "build muscle"


def test_generate_workout_plan_without_goal(client):
    token = _get_token(client)
    _upgrade_to_premium(client, token)

    response = client.post(WORKOUT_PLANS_URL, json={}, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["goal"] is None
    assert data["plan_text"]


# ---------------------------------------------------------------------------
# Nutrition plans
# ---------------------------------------------------------------------------

def test_generate_and_list_nutrition_plan_as_premium(client):
    token = _get_token(client)
    _upgrade_to_premium(client, token)

    response = client.post(
        NUTRITION_PLANS_URL, json={"goal": "vegetarian, high protein"}, headers=_auth(token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["goal"] == "vegetarian, high protein"
    assert data["plan_text"]

    history = client.get(NUTRITION_PLANS_URL, headers=_auth(token)).json()
    assert len(history) == 1
