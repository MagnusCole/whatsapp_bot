from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from ..core.auth import create_access_token
from ..core.config import get_settings

router = APIRouter(prefix="/api")

@router.post("/token")
async def get_token(api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
    settings = get_settings()
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    access_token = create_access_token(
        data={"sub": "test_user"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}