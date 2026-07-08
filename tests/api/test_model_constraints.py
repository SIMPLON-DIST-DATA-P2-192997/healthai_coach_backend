"""Tests for the SQLAlchemy models in api/models against the MLD/MPD contract
described in database/schema/modele_donnees.md and database/schema/ddl_postgres.sql.

Uses its own isolated in-memory SQLite database (independent from the
conftest.py `client`/`db_session` fixtures used by the HTTP-level tests) so
that PRAGMA foreign_keys can be enabled without affecting other suites.
"""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base
from api.models.biometric_measurement import BiometricMeasurement
from api.models.data_quality_log import DataQualityLog
from api.models.diet_recommendation import DietRecommendation
from api.models.dietary_preference import DietaryPreference
from api.models.exercise import Exercise
from api.models.fitness_profile import FitnessProfile
from api.models.food_item import FoodItem
from api.models.medical_profile import MedicalProfile
from api.models.nutrition_log import NutritionLog
from api.models.user import User
from api.models.workout_session import WorkoutSession
from api.models.workout_set import WorkoutSet

NOW = datetime.now(timezone.utc)


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(eng, "connect")
    def _enable_fk(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def session(engine):
    TestingSession = sessionmaker(bind=engine)
    s = TestingSession()
    yield s
    s.close()


def make_user(session, email="user@example.com", **overrides):
    defaults = dict(
        email=email,
        hashed_password="hashed",
        first_name="Jane",
        last_name="Doe",
    )
    defaults.update(overrides)
    user = User(**defaults)
    session.add(user)
    session.commit()
    return user


def make_food_item(session, **overrides):
    defaults = dict(source="test_source", name="Apple", calories_kcal=52)
    defaults.update(overrides)
    item = FoodItem(**defaults)
    session.add(item)
    session.commit()
    return item


def make_exercise(session, **overrides):
    defaults = dict(source="exercisedb", name="Push-up")
    defaults.update(overrides)
    exercise = Exercise(**defaults)
    session.add(exercise)
    session.commit()
    return exercise


# ---------------------------------------------------------------------------
# Table / column names must mirror ddl_postgres.sql (MPD)
# ---------------------------------------------------------------------------

EXPECTED_TABLES_AND_PKS = {
    "users": "user_id",
    "food_items": "food_item_id",
    "nutrition_logs": "log_id",
    "exercises": "exercise_id",
    "workout_sessions": "session_id",
    "workout_sets": "set_id",
    "biometric_measurements": "measurement_id",
    "medical_profiles": "medical_profile_id",
    "dietary_preferences": "dietary_preference_id",
    "fitness_profiles": "fitness_profile_id",
    "diet_recommendations": "diet_recommendation_id",
    "data_quality_log": "dq_log_id",
}


def test_table_names_and_primary_keys_match_ddl(engine):
    """Regression test: DataQualityLog previously mapped to the wrong,
    non-existent 'data_quality_logs' table (missing the 's')."""
    insp = inspect(engine)
    actual_tables = set(insp.get_table_names())
    assert actual_tables == set(EXPECTED_TABLES_AND_PKS)

    for table, expected_pk in EXPECTED_TABLES_AND_PKS.items():
        pk_cols = insp.get_pk_constraint(table)["constrained_columns"]
        assert pk_cols == [expected_pk], f"{table} PK should be {expected_pk!r}, got {pk_cols!r}"


def test_foreign_keys_reference_correct_columns(engine):
    insp = inspect(engine)

    fks = {(fk["constrained_columns"][0]): fk for fk in insp.get_foreign_keys("nutrition_logs")}
    assert fks["user_id"]["referred_table"] == "users"
    assert fks["user_id"]["referred_columns"] == ["user_id"]
    assert fks["food_item_id"]["referred_table"] == "food_items"
    assert fks["food_item_id"]["referred_columns"] == ["food_item_id"]

    (fk,) = insp.get_foreign_keys("data_quality_log")
    assert fk["constrained_columns"] == ["resolved_by"]
    assert fk["referred_table"] == "users"
    assert fk["referred_columns"] == ["user_id"]


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

def test_user_required_fields_are_not_nullable(session):
    with pytest.raises(IntegrityError):
        session.add(User(email="a@b.com", hashed_password="x", first_name=None, last_name="Doe"))
        session.commit()


def test_user_email_must_be_unique(session):
    make_user(session, email="dupe@example.com")
    session.add(User(email="dupe@example.com", hashed_password="x", first_name="A", last_name="B"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_sex_check_constraint_rejects_invalid_value(session):
    session.add(
        User(email="x@example.com", hashed_password="x", first_name="A", last_name="B", sex="invalid")
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_sex_check_constraint_accepts_valid_values(session):
    for i, sex in enumerate(["F", "M", "other"]):
        make_user(session, email=f"sex{i}@example.com", sex=sex)


# ---------------------------------------------------------------------------
# food_items
# ---------------------------------------------------------------------------

def test_food_item_source_and_calories_required(session):
    with pytest.raises(IntegrityError):
        session.add(FoodItem(name="Banana", calories_kcal=None, source="src"))
        session.commit()


def test_food_item_unique_source_and_external_id(session):
    make_food_item(session, source="kaggle", external_id="1")
    session.add(FoodItem(source="kaggle", external_id="1", name="Other", calories_kcal=10))
    with pytest.raises(IntegrityError):
        session.commit()


def test_food_item_calories_check_constraint(session):
    session.add(FoodItem(source="src", name="Bad", calories_kcal=-5))
    with pytest.raises(IntegrityError):
        session.commit()


# ---------------------------------------------------------------------------
# nutrition_logs
# ---------------------------------------------------------------------------

def test_nutrition_log_meal_type_check_constraint(session):
    user = make_user(session)
    food = make_food_item(session)
    session.add(
        NutritionLog(
            user_id=user.id,
            food_item_id=food.id,
            quantity_g=100,
            meal_type="brunch",
            logged_at=NOW,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_nutrition_log_quantity_must_be_positive(session):
    user = make_user(session)
    food = make_food_item(session)
    session.add(
        NutritionLog(
            user_id=user.id, food_item_id=food.id, quantity_g=0, meal_type="lunch", logged_at=NOW
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_nutrition_log_cascades_on_user_delete(session):
    user = make_user(session)
    food = make_food_item(session)
    session.add(
        NutritionLog(
            user_id=user.id, food_item_id=food.id, quantity_g=100, meal_type="lunch", logged_at=NOW
        )
    )
    session.commit()

    session.delete(user)
    session.commit()

    assert session.query(NutritionLog).count() == 0


def test_nutrition_log_restricts_food_item_delete(session):
    user = make_user(session)
    food = make_food_item(session)
    session.add(
        NutritionLog(
            user_id=user.id, food_item_id=food.id, quantity_g=100, meal_type="lunch", logged_at=NOW
        )
    )
    session.commit()

    session.delete(food)
    with pytest.raises(IntegrityError):
        session.commit()


# ---------------------------------------------------------------------------
# exercises / workout_sessions / workout_sets
# ---------------------------------------------------------------------------

def test_exercise_unique_source_and_external_id(session):
    make_exercise(session, source="exercisedb", external_id="e1")
    session.add(Exercise(source="exercisedb", external_id="e1", name="Other"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_workout_session_ended_at_must_be_after_started_at(session):
    user = make_user(session)
    session.add(
        WorkoutSession(
            user_id=user.id,
            started_at=NOW,
            ended_at=NOW - timedelta(hours=1),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_workout_session_bpm_must_be_positive(session):
    user = make_user(session)
    session.add(WorkoutSession(user_id=user.id, started_at=NOW, max_bpm=0))
    with pytest.raises(IntegrityError):
        session.commit()


def test_workout_set_unique_session_exercise_set_number(session):
    user = make_user(session)
    exercise = make_exercise(session)
    ws = WorkoutSession(user_id=user.id, started_at=NOW)
    session.add(ws)
    session.commit()

    session.add(WorkoutSet(session_id=ws.id, exercise_id=exercise.id, set_number=1))
    session.commit()

    session.add(WorkoutSet(session_id=ws.id, exercise_id=exercise.id, set_number=1))
    with pytest.raises(IntegrityError):
        session.commit()


def test_workout_set_set_number_must_be_positive(session):
    user = make_user(session)
    exercise = make_exercise(session)
    ws = WorkoutSession(user_id=user.id, started_at=NOW)
    session.add(ws)
    session.commit()

    session.add(WorkoutSet(session_id=ws.id, exercise_id=exercise.id, set_number=0))
    with pytest.raises(IntegrityError):
        session.commit()


def test_workout_set_cascades_on_session_delete(session):
    user = make_user(session)
    exercise = make_exercise(session)
    ws = WorkoutSession(user_id=user.id, started_at=NOW)
    session.add(ws)
    session.commit()
    session.add(WorkoutSet(session_id=ws.id, exercise_id=exercise.id, set_number=1))
    session.commit()

    session.delete(ws)
    session.commit()

    assert session.query(WorkoutSet).count() == 0


def test_workout_set_restricts_exercise_delete(session):
    user = make_user(session)
    exercise = make_exercise(session)
    ws = WorkoutSession(user_id=user.id, started_at=NOW)
    session.add(ws)
    session.commit()
    session.add(WorkoutSet(session_id=ws.id, exercise_id=exercise.id, set_number=1))
    session.commit()

    session.delete(exercise)
    with pytest.raises(IntegrityError):
        session.commit()


# ---------------------------------------------------------------------------
# biometric_measurements / medical_profiles / fitness_profiles / diet_recommendations
# ---------------------------------------------------------------------------

def test_biometric_measurement_unique_user_and_measured_at(session):
    user = make_user(session)
    session.add(BiometricMeasurement(user_id=user.id, measured_at=NOW, weight_kg=70))
    session.commit()

    session.add(BiometricMeasurement(user_id=user.id, measured_at=NOW, weight_kg=71))
    with pytest.raises(IntegrityError):
        session.commit()


def test_biometric_measurement_body_fat_pct_range_check(session):
    user = make_user(session)
    session.add(BiometricMeasurement(user_id=user.id, measured_at=NOW, body_fat_pct=150))
    with pytest.raises(IntegrityError):
        session.commit()


def test_medical_profile_severity_check_constraint(session):
    user = make_user(session)
    session.add(MedicalProfile(user_id=user.id, severity="Extreme", recorded_at=NOW))
    with pytest.raises(IntegrityError):
        session.commit()


def test_fitness_profile_workout_frequency_range_check(session):
    user = make_user(session)
    session.add(
        FitnessProfile(user_id=user.id, workout_frequency_days_per_week=8, recorded_at=NOW)
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_diet_recommendation_adherence_range_check(session):
    user = make_user(session)
    session.add(
        DietRecommendation(user_id=user.id, adherence_to_diet_plan_pct=101, recommended_at=NOW)
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_dietary_preference_cascades_on_user_delete(session):
    user = make_user(session)
    session.add(DietaryPreference(user_id=user.id, preferred_cuisine="Mexican", recorded_at=NOW))
    session.commit()

    session.delete(user)
    session.commit()

    assert session.query(DietaryPreference).count() == 0


# ---------------------------------------------------------------------------
# data_quality_log
# ---------------------------------------------------------------------------

def test_data_quality_log_severity_check_constraint(session):
    session.add(
        DataQualityLog(
            source_table="food_items", rule_name="not_null_check", severity="fatal", message="x"
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_quality_log_resolution_consistency_check(session):
    """resolved_at/resolved_by can only be set when resolved = TRUE."""
    session.add(
        DataQualityLog(
            source_table="food_items",
            rule_name="not_null_check",
            severity="warning",
            message="x",
            resolved=False,
            resolved_at=NOW,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_quality_log_resolved_by_set_null_on_user_delete(session):
    admin = make_user(session, email="admin@example.com")
    log = DataQualityLog(
        source_table="food_items",
        rule_name="not_null_check",
        severity="warning",
        message="x",
        resolved=True,
        resolved_at=NOW,
        resolved_by=admin.id,
    )
    session.add(log)
    session.commit()

    session.delete(admin)
    session.commit()

    session.refresh(log)
    assert log.resolved_by is None
