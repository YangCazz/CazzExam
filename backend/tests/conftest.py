import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from pathlib import Path
from app.config import settings
settings.db_path = Path(__file__).parent / "test_study.db"
if settings.db_path.exists():
    settings.db_path.unlink()
from fastapi.testclient import TestClient
from app.main import app
import pytest


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
