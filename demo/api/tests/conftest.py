import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TNZ_AUTH_TOKEN", "test-token")
    monkeypatch.setenv("TNZ_API_URL", "https://api.tnz.co.nz/api/v3.00")
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)
    return TestClient(app)
