import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app
from src.services.message import MessageService
from src.core.database import get_db

# Remove any test_token fixture definition here if it exists

@pytest.fixture
def test_client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    return TestClient(app)

# Remove @pytest.mark.asyncio from test functions that use TestClient
def test_send_message(test_client, test_token):
    """Test sending a message through the API"""
    headers = {"Authorization": f"Bearer {test_token}"}
    message_data = {
        "content": "Test message",
        "receiver_id": "test_receiver",
        "message_type": "text"
    }
    
    response = test_client.post(
        "/api/messages",
        json=message_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == message_data["content"]
    assert data["receiver_id"] == message_data["receiver_id"]
    assert data["sender_id"] == "test_user"

def test_get_message(test_client, test_token):
    """Test retrieving a specific message"""
    # Create message first using the API
    message_data = {
        "content": "Test message for retrieval",
        "receiver_id": "test_receiver",
        "message_type": "text"
    }
    
    headers = {"Authorization": f"Bearer {test_token}"}
    create_response = test_client.post("/api/messages", json=message_data, headers=headers)
    message = create_response.json()
    
    # Get the created message
    response = test_client.get(f"/api/messages/{message['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message["id"]
    assert data["content"] == message["content"]

def test_get_conversation(test_client, test_token):
    """Test getting conversation between two users"""
    # Create test messages first
    headers = {"Authorization": f"Bearer {test_token}"}
    message_data = {
        "content": "Test conversation message",
        "receiver_id": "user123",
        "message_type": "text"
    }
    
    # Create a message
    test_client.post("/api/messages", json=message_data, headers=headers)
    
    # Get conversation
    response = test_client.get("/api/conversations/user123", headers=headers)
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)
    assert len(messages) > 0

def test_update_message_status(test_client, test_token):
    """Test updating message status"""
    # Create message first
    message_data = {
        "content": "Test message for status update",
        "receiver_id": "test_receiver",
        "message_type": "text"
    }
    
    headers = {"Authorization": f"Bearer {test_token}"}
    create_response = test_client.post("/api/messages", json=message_data, headers=headers)
    message = create_response.json()
    
    # Update status
    response = test_client.put(
        f"/api/messages/{message['id']}/status?status=read",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    
    # Get updated message to verify status
    get_response = test_client.get(f"/api/messages/{message['id']}", headers=headers)
    updated_message = get_response.json()
    assert updated_message["status"] == "read"

def test_get_messages_with_api_key(test_client, test_api_key, clean_db):
    """Test getting all messages with API key authentication"""
    # First create a test message using token auth
    headers = {"X-API-Key": test_api_key}
    
    # Get all messages
    response = test_client.get("/api/messages", headers=headers)
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)

@pytest.fixture
def message_service(test_db):
    """Fixture for MessageService instance"""
    return MessageService(test_db)