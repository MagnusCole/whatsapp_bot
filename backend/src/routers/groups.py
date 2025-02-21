from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..core.security import get_current_user
from ..models.user import User
from ..services.group import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None

class GroupMemberAdd(BaseModel):
    user_id: int
    role: str = "member"

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    avatar_url: Optional[str]
    created_by: int
    created_at: datetime
    member_count: int
    is_active: bool

    class Config:
        orm_mode = True

class GroupMemberResponse(BaseModel):
    user_id: int
    group_id: int
    role: str
    joined_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.create_group(current_user.id, group_data)

@router.get("/", response_model=List[GroupResponse])
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.get_user_groups(current_user.id, skip=skip, limit=limit)

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    group = await group_service.get_group(group_id, current_user.id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found or access denied"
        )
    return group

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    update_data: GroupUpdate,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.update_group(group_id, current_user.id, update_data)

@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def add_group_member(
    group_id: int,
    member_data: GroupMemberAdd,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.add_member(group_id, current_user.id, member_data)

@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    success = await group_service.remove_member(group_id, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found or permission denied"
        )

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def list_group_members(
    group_id: int,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.get_group_members(group_id, current_user.id)

@router.get("/{group_id}/stats", response_model=dict)
async def get_group_stats(
    group_id: int,
    current_user: User = Depends(get_current_user)
):
    group_service = GroupService()
    return await group_service.get_group_statistics(group_id, current_user.id)