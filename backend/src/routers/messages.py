from fastapi import APIRouter, Depends, HTTPException, Security, status  # Add Security
from typing import List, Dict, Optional
from ..core.auth import verify_token, verify_api_key
from ..services.message import MessageService, MessageResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.logging_config import get_logger  # Add this import

logger = get_logger(__name__)  # Add this line
router = APIRouter(prefix="/api")

# Request/Response models
class MessageCreate(BaseModel):
    content: str
    receiver_id: str
    message_type: str = "text"
    metadata: Optional[Dict] = None

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Security, 
    status,
    BackgroundTasks
)
from typing import List, Dict, Optional

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Security(verify_api_key),
    token_data: Optional[dict] = Security(verify_token),
    background_tasks: BackgroundTasks = None
):
    try:
        service = MessageService(db)
        sender_id = token_data["sub"] if token_data else "api_client"
        
        created_message = await service.create_message(
            content=message.content,
            sender_id=sender_id,
            receiver_id=message.receiver_id,
            message_type=message.message_type,
            metadata=message.metadata
        )
        
        # Send to middleware
        background_tasks.add_task(
            service.send_to_middleware,
            created_message
        )
        
        return created_message
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),  # AsyncSession como dependencia
    token_data = Depends(verify_token)
):
    service = MessageService(db)
    message = await service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message  # Retorna el mensaje, no la sesión

@router.get("/conversations/{other_user_id}", response_model=List[MessageResponse])
async def get_conversation(
    other_user_id: str,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    service = MessageService(db)
    return await service.get_conversation(token_data["sub"], other_user_id)

@router.put("/messages/{message_id}/status")
async def update_message_status(
    message_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    service = MessageService(db)
    success = await service.update_message_status(message_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "updated"}

from typing import Union

async def verify_auth(
    api_key: str = Depends(verify_api_key, use_cache=True),
    token: dict = Depends(verify_token, use_cache=True)
) -> Union[str, dict]:
    """Verify either API key or token authentication"""
    return api_key or token

@router.get("/messages")
async def get_messages(
    db: AsyncSession = Depends(get_db),
    auth: Union[str, dict] = Depends(verify_auth)
):
    """Get all messages. Accepts both API key and JWT token authentication."""
    service = MessageService(db)
    return await service.get_messages()