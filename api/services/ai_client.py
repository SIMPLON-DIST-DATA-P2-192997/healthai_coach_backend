"""Client for the AI recommendation microservice.

The microservice isn't deployed yet, so every function here returns a
deterministic stub instead of making a network call. Each one is written the
way the real call will look — same signature, same return shape — so that
swapping the stub body for an `httpx` call to `settings.AI_SERVICE_URL` is a
localized change: nothing in the routers/CRUD layer above has to change.

`settings.AI_SERVICE_URL` (currently unset) marks where the real base URL
will come from once the microservice is deployed.
"""


def generate_diet_recommendation(goal: str | None) -> dict:
    """Return the fields expected by DietRecommendationCreate.

    TODO(ai-service): once AI_SERVICE_URL is set, replace this stub with:
        response = httpx.post(f"{settings.AI_SERVICE_URL}/diet-recommendations", json={"goal": goal})
        return response.json()
    """
    del goal  # unused by the stub; the real call will forward it
    return {
        "daily_caloric_intake_kcal": 2000.0,
        "adherence_to_diet_plan_pct": None,
        "dietary_nutrient_imbalance_score": None,
        "recommendation": "Balanced",
    }


def generate_workout_plan(goal: str | None) -> str:
    """Return the plan_text for a WorkoutPlan.

    TODO(ai-service): once AI_SERVICE_URL is set, replace this stub with:
        response = httpx.post(f"{settings.AI_SERVICE_URL}/workout-plans", json={"goal": goal})
        return response.json()["plan_text"]
    """
    if goal:
        return f"Placeholder workout plan for goal '{goal}': 3x/week full-body strength training, 20min cardio."
    return "Placeholder workout plan: 3x/week full-body strength training, 20min cardio."


def generate_nutrition_plan(goal: str | None) -> str:
    """Return the plan_text for a NutritionPlan.

    TODO(ai-service): once AI_SERVICE_URL is set, replace this stub with:
        response = httpx.post(f"{settings.AI_SERVICE_URL}/nutrition-plans", json={"goal": goal})
        return response.json()["plan_text"]
    """
    if goal:
        return f"Placeholder nutrition plan for goal '{goal}': balanced macros, 3 meals + 1 snack/day."
    return "Placeholder nutrition plan: balanced macros, 3 meals + 1 snack/day."
