import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from src.core.auth import create_access_token, create_api_key
from src.core.config import get_settings
from src.main import app

settings = get_settings()

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_api_key():
    return create_api_key()  # This will now create a proper JWT token

@pytest.fixture
def test_user_token():
    return create_access_token(
        data={"sub": "testuser"},
        expires_delta=timedelta(minutes=30)
    )

def test_api_key_auth(test_client, test_api_key):
    """Test API key authentication"""
    headers = {"X-API-Key": test_api_key}  # Use direct header name
    response = test_client.get("/api/messages", headers=headers)
    assert response.status_code in [200, 404]

def test_token_auth(test_client, test_user_token):
    """Test JWT token authentication"""
    headers = {"Authorization": f"Bearer {test_user_token}"}  # Add Bearer prefix back
    response = test_client.get("/api/messages", headers=headers)
    assert response.status_code in [200, 404]