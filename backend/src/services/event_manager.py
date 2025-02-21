from typing import Dict, Optional, List, Callable, Any
from fastapi import WebSocket, BackgroundTasks
import asyncio
import json
import logging
import aiohttp
from datetime import datetime, UTC  # Add UTC import here
from ..models.message import Message
from ..core.logging_config import get_logger

logger = logging.getLogger(__name__)

class EventManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.webhook_urls: Dict[str, str] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.background_tasks: BackgroundTasks = BackgroundTasks()
        self._queue_task: Optional[asyncio.Task] = None

    async def register_websocket(self, client_id: str, websocket: WebSocket):
        try:
            await websocket.accept()
            if client_id in self.active_connections:
                # Close existing connection if any
                try:
                    await self.active_connections[client_id].close()
                except:
                    pass
            self.active_connections[client_id] = websocket
            logger.info(f"Client {client_id} connected via WebSocket")
        except Exception as e:
            logger.error(f"Error registering WebSocket for client {client_id}: {str(e)}")
            raise

    def register_webhook(self, client_id: str, webhook_url: str):
        self.webhook_urls[client_id] = webhook_url
        logger.info(f"Client {client_id} registered webhook at {webhook_url}")

    async def broadcast_message(self, message: Dict[str, Any]):
        # Add message to queue for processing
        await self.message_queue.put(message)
        
        # Process WebSocket delivery
        websocket_tasks = []
        for client_id, ws in self.active_connections.items():
            task = asyncio.create_task(self._send_ws_message(client_id, ws, message))
            websocket_tasks.append(task)
        
        # Process webhook delivery for clients without active WebSocket
        webhook_tasks = []
        for client_id, url in self.webhook_urls.items():
            if client_id not in self.active_connections:
                task = asyncio.create_task(self._send_webhook(client_id, url, message))
                webhook_tasks.append(task)
        
        # Wait for all deliveries to complete
        await asyncio.gather(*websocket_tasks, *webhook_tasks)

    async def _send_ws_message(self, client_id: str, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_text(json.dumps(message))
            logger.info(f"Message sent to client {client_id} via WebSocket")
        except Exception as e:
            logger.error(f"WebSocket delivery failed for client {client_id}: {str(e)}")
            # Remove failed connection and try webhook fallback
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.webhook_urls:
                await self._send_webhook(client_id, self.webhook_urls[client_id], message)

    async def _send_webhook(self, client_id: str, webhook_url: str, message: Dict[str, Any]):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        logger.info(f"Message sent to client {client_id} via webhook")
                    else:
                        logger.error(f"Webhook delivery failed for client {client_id}: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Webhook delivery failed for client {client_id}: {str(e)}")

    async def process_message_queue(self):
        while True:
            try:
                message = await self.message_queue.get()
                await self.broadcast_message(message)
                self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message queue: {str(e)}")
            await asyncio.sleep(0.1)  # Prevent CPU overload

    def start_background_tasks(self):
        if self._queue_task is None or self._queue_task.done():
            self._queue_task = asyncio.create_task(self.process_message_queue())

    async def cleanup_connection(self, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except:
                pass
            del self.active_connections[client_id]
            logger.info(f"Cleaned up connection for client {client_id}")

    async def close_all_connections(self):
        for client_id in list(self.active_connections.keys()):
            await self.cleanup_connection(client_id)
        if self._queue_task and not self._queue_task.done():
            self._queue_task.cancel()
            try:
                await self._queue_task
            except asyncio.CancelledError:
                pass

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]):
        try:
            # Enhance message with metadata
            enhanced_message = {
                "type": "message",
                "client_id": client_id,
                "content": message,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            # Broadcast to all clients
            await self.broadcast_message(enhanced_message)
            
            return True
        except Exception as e:
            logger.error(f"Error handling message from client {client_id}: {str(e)}")
            return False

    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection and message processing"""
        try:
            await websocket.accept()
            # Send initial connection success message
            await websocket.send_json({"status": "connected"})
            
            while True:
                try:
                    data = await websocket.receive_json()
                    await self.handle_client_message("default", data)
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {str(e)}")
                    break
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
        finally:
            await self.cleanup_connection("default")

# Create a singleton instance
event_manager = EventManager()