from datetime import datetime
from typing import Optional
from drizzle_orm import *
from drizzle_orm.pg_core import *

# Users table
class Users(Table):
    id = serial('id').primary_key()
    name = text('name').not_null()
    phone = text('phone').not_null().unique()
    api_key = text('api_key').not_null().unique()
    created_at = timestamp('created_at').default(datetime.utcnow)
    updated_at = timestamp('updated_at').default(datetime.utcnow)

# Messages table - Optimized for high volume
class Messages(Table):
    id = bigserial('id').primary_key()  # Using bigserial for high volume
    user_id = integer('user_id').references(Users.id)
    content = text('content').not_null()
    status = text('status').not_null().default('pending')  # pending, sent, delivered, read
    timestamp = timestamp('timestamp').default(datetime.utcnow).index()  # Indexed for faster queries
    metadata = jsonb('metadata').default({})  # For extensibility

    class Meta:
        indexes = [
            Index('messages_user_timestamp_idx', 'user_id', 'timestamp'),  # Optimize message history queries
            Index('messages_status_idx', 'status')  # Optimize status-based queries
        ]

# Sessions table
class Sessions(Table):
    id = serial('id').primary_key()
    user_id = integer('user_id').references(Users.id)
    connection_status = text('connection_status').not_null().default('offline')  # offline, online, away
    timestamp = timestamp('timestamp').default(datetime.utcnow)
    last_activity = timestamp('last_activity').default(datetime.utcnow)
    device_info = jsonb('device_info').default({})  # Store device-specific information

    class Meta:
        indexes = [
            Index('sessions_user_status_idx', 'user_id', 'connection_status')  # Optimize online status queries
        ]

# Conversations table
class Conversations(Table):
    id = serial('id').primary_key()
    user_id = integer('user_id').references(Users.id)
    status = text('status').not_null().default('active')  # active, archived, deleted
    last_activity = timestamp('last_activity').default(datetime.utcnow)
    participant_ids = array('participant_ids', integer)  # Array of user IDs in the conversation
    metadata = jsonb('metadata').default({})  # Store conversation settings, pins, etc.

    class Meta:
        indexes = [
            Index('conversations_user_activity_idx', 'user_id', 'last_activity'),  # Optimize recent conversations queries
            Index('conversations_status_idx', 'status')  # Optimize status-based filtering
        ]