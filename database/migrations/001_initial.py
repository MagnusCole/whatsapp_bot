from drizzle_orm import PostgresDatabase
from drizzle_orm.pg_core import *
from datetime import datetime

def upgrade(db: PostgresDatabase):
    # Create Users table
    db.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        api_key TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create Messages table with optimizations for high volume
    db.execute("""
    CREATE TABLE messages (
        id BIGSERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        content TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB DEFAULT '{}'
    );
    CREATE INDEX messages_user_timestamp_idx ON messages(user_id, timestamp);
    CREATE INDEX messages_status_idx ON messages(status);
    """)

    # Create Sessions table
    db.execute("""
    CREATE TABLE sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        connection_status TEXT NOT NULL DEFAULT 'offline',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        device_info JSONB DEFAULT '{}'
    );
    CREATE INDEX sessions_user_status_idx ON sessions(user_id, connection_status);
    """)

    # Create Conversations table
    db.execute("""
    CREATE TABLE conversations (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        status TEXT NOT NULL DEFAULT 'active',
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        participant_ids INTEGER[],
        metadata JSONB DEFAULT '{}'
    );
    CREATE INDEX conversations_user_activity_idx ON conversations(user_id, last_activity);
    CREATE INDEX conversations_status_idx ON conversations(status);
    """)

def downgrade(db: PostgresDatabase):
    # Drop tables in reverse order to handle dependencies
    db.execute("DROP TABLE IF EXISTS conversations CASCADE;")
    db.execute("DROP TABLE IF EXISTS sessions CASCADE;")
    db.execute("DROP TABLE IF EXISTS messages CASCADE;")
    db.execute("DROP TABLE IF EXISTS users CASCADE;")