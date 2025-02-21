from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, UTC
from .base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    connection_status = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=lambda: datetime.now(UTC))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))