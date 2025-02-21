from datetime import datetime, UTC  # Add UTC import
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import TIMESTAMP
from .base import Base

class TimestampWithTimeZone(TypeDecorator):
    impl = TIMESTAMP(timezone=True)
    cache_ok = True

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    message_type = Column(String)
    status = Column(String, default="sent")
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }