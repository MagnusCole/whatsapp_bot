from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..core.security import get_current_user
from ..models.user import User
from ..services.session import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionResponse(BaseModel):
    id: int
    user_id: int
    device_info: Optional[str]
    last_active: datetime
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class SessionCreate(BaseModel):
    device_info: Optional[str] = None

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService()
    return await session_service.create_session(current_user.id, session_data)

@router.get("/active", response_model=List[SessionResponse])
async def list_active_sessions(
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService()
    return await session_service.get_active_sessions(current_user.id)

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService()
    success = await session_service.terminate_session(session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already terminated"
        )

@router.get("/stats", response_model=dict)
async def get_session_stats(
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService()
    return await session_service.get_session_statistics(current_user.id)