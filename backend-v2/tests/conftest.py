import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.api.v1.endpoints.auth import get_current_user, UserInfoResponse
import os

# Use a test database
os.environ["DATABASE_URL_OVERRIDE"] = "sqlite:///./test_smoke.db"

engine = create_engine("sqlite:///./test_smoke.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_smoke.db"):
        os.remove("./test_smoke.db")

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return UserInfoResponse(
        id="test_user_123",
        username="test_user",
        name="Test User",
        role="admin"
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
