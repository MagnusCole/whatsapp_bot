from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from ..models.message import Message
from pydantic import BaseModel

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: str
    receiver_id: str
    message_type: str
    status: str
    metadata: Dict = {}
    created_at: str

    @classmethod
    def from_orm(cls, message: Message):
        return cls(
            id=message.id,
            content=message.content,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            message_type=message.message_type,
            status=message.status,
            metadata={},
            created_at=message.created_at.isoformat()
        )

from datetime import datetime, UTC
import websockets
import json
from ..core.logging_config import get_logger
from ..core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

class MessageService:
    def __init__(self, db):
        self.db = db
        # Update WebSocket URL to match middleware configuration
        self.middleware_ws_url = "ws://localhost:8080/ws"  # Changed from 3000 to 8080

    async def create_message(self, content: str, sender_id: str, receiver_id: str, message_type: str = "text", metadata: Optional[Dict] = None) -> MessageResponse:
        message = Message(
            content=content,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            status="sent",
            metadata=metadata or {},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return MessageResponse.from_orm(message)

    async def update_message_status(self, message_id: int, status: str) -> bool:
        query = select(Message).where(Message.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            return False
            
        message.status = status
        message.updated_at = datetime.now(UTC)  # Use UTC-aware datetime
        await self.db.commit()
        return True

    async def get_messages(self, user_id: Optional[str] = None) -> List[MessageResponse]:
        query = select(Message)
        if user_id:
            query = query.where(Message.sender_id == user_id)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        return [MessageResponse.from_orm(msg) for msg in messages]

    async def get_message(self, message_id: int) -> Optional[MessageResponse]:
        query = select(Message).where(Message.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        return MessageResponse.from_orm(message) if message else None

    async def get_conversation(self, user1_id: str, user2_id: str) -> List[MessageResponse]:
        query = select(Message).where(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
            )
        ).order_by(Message.created_at.desc())
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        return [MessageResponse.from_orm(msg) for msg in messages]

    async def update_message_status(self, message_id: int, status: str) -> bool:
        query = select(Message).where(Message.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            return False
            
        message.status = status
        await self.db.commit()
        return True

    async def send_to_middleware(self, message):
        """Send message to middleware via WebSocket"""
        try:
            async with websockets.connect(self.middleware_ws_url) as websocket:
                metadata = message.metadata or {}
                message_data = {
                    "content": message.content,
                    "to": f"{message.receiver_id}@s.whatsapp.net",  # Number should already include country code
                    "type": "text",  # Baileys expects "text" for text messages
                    "metadata": {
                        "id": str(message.id),
                        "sender_id": message.sender_id,
                        "original_type": message.message_type,
                        **metadata
                    }
                }
                await websocket.send(json.dumps(message_data))
                response = await websocket.recv()
                logger.info(f"Middleware response: {response}")
                
        except Exception as e:
            logger.error(f"Error sending message to middleware: {str(e)}", exc_info=True)
            # Don't raise the exception - this is a background task