from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, status

from api.core.deps import CurrentPremiumUser, DB
from api.crud.health_profile import create_diet_recommendation
from api.crud.nutrition_plan import create_nutrition_plan, get_nutrition_plans_by_user
from api.crud.workout_plan import create_workout_plan, get_workout_plans_by_user
from api.schemas.ai import AIGenerationRequest
from api.schemas.diet_recommendation import DietRecommendationCreate, DietRecommendationRead
from api.schemas.nutrition_plan import NutritionPlanRead
from api.schemas.workout_plan import WorkoutPlanRead
from api.services import ai_client

router = APIRouter(prefix="/ai", tags=["ai"])


# ---------------------------------------------------------------------------
# Diet recommendations
#
# Listing stays under GET /health-profiles/diet-recommendations (existing
# endpoint, same table) — only the generation action is new here.
# ---------------------------------------------------------------------------

@router.post(
    "/diet-recommendations",
    response_model=DietRecommendationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a diet recommendation",
    description="Generate a new diet recommendation for the authenticated user via the AI "
    "microservice. Requires an active premium/premium_plus/b2b subscription. The microservice "
    "isn't deployed yet: this currently returns a placeholder recommendation (see "
    "`api/services/ai_client.py`), but the request/response contract will stay the same once "
    "the real service is wired in.",
)
def generate_diet_recommendation_endpoint(
    data_in: AIGenerationRequest, current_user: CurrentPremiumUser, db: DB
) -> DietRecommendationRead:
    result = ai_client.generate_diet_recommendation(data_in.goal)
    rec_in = DietRecommendationCreate(recommended_at=datetime.now(timezone.utc), **result)
    return create_diet_recommendation(db, current_user.id, rec_in)  # type: ignore[return-value,arg-type]


# ---------------------------------------------------------------------------
# Workout plans
# ---------------------------------------------------------------------------

@router.get(
    "/workout-plans",
    response_model=List[WorkoutPlanRead],
    summary="List my AI workout plans",
    description="Return workout plans previously generated for the authenticated user, most "
    "recent first. Requires an active premium/premium_plus/b2b subscription.",
)
def list_my_workout_plans(
    skip: int = 0, limit: int = 100,
    current_user: CurrentPremiumUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[WorkoutPlanRead]:
    return get_workout_plans_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value,arg-type]


@router.post(
    "/workout-plans",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a workout plan",
    description="Generate a new workout plan for the authenticated user via the AI "
    "microservice. Requires an active premium/premium_plus/b2b subscription. `goal` is passed "
    "through to the microservice, e.g. 'lose weight', 'build muscle'. Currently returns a "
    "placeholder plan (see `api/services/ai_client.py`) since the microservice isn't deployed "
    "yet.",
)
def generate_workout_plan_endpoint(
    data_in: AIGenerationRequest, current_user: CurrentPremiumUser, db: DB
) -> WorkoutPlanRead:
    plan_text = ai_client.generate_workout_plan(data_in.goal)
    return create_workout_plan(db, current_user.id, data_in.goal, plan_text)  # type: ignore[return-value,arg-type]


# ---------------------------------------------------------------------------
# Nutrition plans
# ---------------------------------------------------------------------------

@router.get(
    "/nutrition-plans",
    response_model=List[NutritionPlanRead],
    summary="List my AI nutrition plans",
    description="Return nutrition plans previously generated for the authenticated user, most "
    "recent first. Requires an active premium/premium_plus/b2b subscription.",
)
def list_my_nutrition_plans(
    skip: int = 0, limit: int = 100,
    current_user: CurrentPremiumUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[NutritionPlanRead]:
    return get_nutrition_plans_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value,arg-type]


@router.post(
    "/nutrition-plans",
    response_model=NutritionPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a nutrition plan",
    description="Generate a new nutrition plan for the authenticated user via the AI "
    "microservice. Requires an active premium/premium_plus/b2b subscription. `goal` is passed "
    "through to the microservice, e.g. 'vegetarian, high protein'. Currently returns a "
    "placeholder plan (see `api/services/ai_client.py`) since the microservice isn't deployed "
    "yet.",
)
def generate_nutrition_plan_endpoint(
    data_in: AIGenerationRequest, current_user: CurrentPremiumUser, db: DB
) -> NutritionPlanRead:
    plan_text = ai_client.generate_nutrition_plan(data_in.goal)
    return create_nutrition_plan(db, current_user.id, data_in.goal, plan_text)  # type: ignore[return-value,arg-type]
