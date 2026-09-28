import os
os.environ["DATABASE_URL"]="sqlite:///./data/test_pocketsmart.db"
os.environ["SECRET_KEY"]="test-secret-key-012345678901234567890123456789"
os.environ["GEMINI_API_KEY"]=""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c: yield c
