import pytest
import json
from fastapi.testclient import TestClient
from src.main import app
from src.services.event_manager import event_manager

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection(mock_websocket_client):
    """Test WebSocket connection and basic message handling"""
    client_id = "test_client"
    await event_manager.register_websocket(client_id, mock_websocket_client)
    assert client_id in event_manager.active_connections
    assert mock_websocket_client.accepted is True

@pytest.mark.asyncio
async def test_websocket_message_broadcast(mock_websocket_client):
    """Test broadcasting messages to connected WebSocket clients"""
    client_id = "test_client"
    await event_manager.register_websocket(client_id, mock_websocket_client)
    
    test_message = {"type": "message", "content": "test broadcast"}
    await event_manager.broadcast_message(test_message)
    
    assert mock_websocket_client.last_message is not None
    assert json.loads(mock_websocket_client.last_message)["content"] == "test broadcast"

@pytest.mark.asyncio
async def test_websocket_client_disconnect(mock_websocket_client):
    """Test proper handling of client disconnection"""
    client_id = "test_client"
    await event_manager.register_websocket(client_id, mock_websocket_client)
    await event_manager.cleanup_connection(client_id)
    
    assert client_id not in event_manager.active_connections
    assert mock_websocket_client.accepted is False

@pytest.mark.asyncio
async def test_websocket_reconnection(mock_websocket_client):
    """Test client reconnection handling"""
    client_id = "test_client"
    # First connection
    await event_manager.register_websocket(client_id, mock_websocket_client)
    
    # Create new connection (should replace old one)
    new_mock_client = mock_websocket_client.__class__()  # Use the class from the fixture
    await event_manager.register_websocket(client_id, new_mock_client)
    
    assert client_id in event_manager.active_connections
    assert event_manager.active_connections[client_id] == new_mock_client
    assert mock_websocket_client.accepted is False

@pytest.mark.asyncio
async def test_websocket_message_handling(mock_websocket_client):
    """Test message handling through WebSocket"""
    client_id = "test_client"
    await event_manager.register_websocket(client_id, mock_websocket_client)
    
    message = {"type": "test", "data": "hello"}
    success = await event_manager.handle_client_message(client_id, message)
    
    assert success is True
    assert mock_websocket_client.last_message is not None
    received_message = json.loads(mock_websocket_client.last_message)
    assert received_message["content"]["type"] == "test"