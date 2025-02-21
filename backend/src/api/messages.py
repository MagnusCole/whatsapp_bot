from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from typing import List, Dict, Optional
from ..core.auth import verify_token, verify_api_key
from ..services.message import MessageService
from pydantic import BaseModel

router = APIRouter()

# WebSocket connections store
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

# Request/Response models
class MessageCreate(BaseModel):
    content: str
    receiver_id: str
    message_type: str = "text"
    metadata: Optional[Dict] = None

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: str
    receiver_id: str
    message_type: str
    status: str
    metadata: Dict
    created_at: str

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Process received message
            # You can add message handling logic here
            await manager.send_message({"status": "received", "data": data}, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    service: MessageService = Depends(),
    token_data = Depends(verify_token)
):
    created_message = await service.create_message(
        content=message.content,
        sender_id=token_data.username,
        receiver_id=message.receiver_id,
        message_type=message.message_type,
        metadata=message.metadata
    )
    
    # Notify receiver through WebSocket if connected
    await manager.send_message(
        {"type": "new_message", "message": created_message.dict()},
        message.receiver_id
    )
    
    return created_message

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    service: MessageService = Depends(),
    token_data = Depends(verify_token)
):
    message = await service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/conversations/{other_user_id}", response_model=List[MessageResponse])
async def get_conversation(
    other_user_id: str,
    service: MessageService = Depends(),
    token_data = Depends(verify_token)
):
    return await service.get_conversation(token_data.username, other_user_id)

@router.put("/messages/{message_id}/status")
async def update_message_status(
    message_id: int,
    status: str,
    service: MessageService = Depends(),
    api_key: str = Depends(verify_api_key)
):
    success = await service.update_message_status(message_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "updated"}