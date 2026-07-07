"""
Shared fixtures for API tests.

Uses an in-memory SQLite database so no running PostgreSQL is required.
The DATABASE_URL env var is forced to SQLite before any api module is
imported, so settings / engine / lifespan all use the same in-memory DB.
"""
import os

# Must be set BEFORE any api imports so pydantic-settings picks it up
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import api.database as _db_module
import api.main as _main_module
from api.database import Base
from api.main import app
from api.core.deps import get_db


# ---------------------------------------------------------------------------
# Single shared in-memory SQLite engine (StaticPool = one connection for all)
# ---------------------------------------------------------------------------

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Patch both module references so the lifespan and SessionLocal use SQLite
_db_module.engine = _test_engine
_main_module.engine = _test_engine
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
_db_module.SessionLocal = _TestingSessionLocal

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the whole test session."""
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate all tables between tests to keep isolation."""
    yield
    with _test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture()
def db_session():
    """Provide a DB session backed by the test SQLite engine."""
    session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient with the DB dependency overridden to use the test session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
