from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json
from pathlib import Path

from .core.auth import get_api_key, verify_token
from .core.config import Settings, get_settings
from .core.logging_config import setup_logging
from .core.middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware, APIKeyValidationError
from .core.queue import get_queue_client
from .services.event_manager import event_manager
from .routers import messages  # Add this import
from .routers import auth

app = FastAPI(title="Messaging Bot Backend")

# Configure CORS and middleware
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
# Remove global dependency and let each endpoint handle its own auth
app.include_router(messages.router)
app.include_router(auth.router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        await event_manager.register_websocket(client_id, websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await event_manager.handle_client_message(client_id, message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from client {client_id}")
                continue
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                break
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
    finally:
        await event_manager.cleanup_connection(client_id)

@app.post("/webhook/register/{client_id}", dependencies=[Depends(get_api_key)])
async def register_webhook(client_id: str, webhook_url: str):
    try:
        event_manager.register_webhook(client_id, webhook_url)
        return {"status": "success", "message": f"Webhook registered for client {client_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Initialize queue client
queue_client = None

# Start background tasks when the application starts
@app.on_event("startup")
async def startup_event():
    global queue_client
    settings = get_settings()
    queue_client = get_queue_client(settings)
    await queue_client.connect()
    event_manager.start_background_tasks()

# Cleanup when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    try:
        await event_manager.close_all_connections()
        if queue_client:
            await queue_client.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)