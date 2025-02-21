from locust import HttpUser, task, between
from typing import Dict
import json
import random

class WhatsAppUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        # Simulate user registration/login
        self.user_id = str(random.randint(1, 1000))
        self.api_key = f"test_api_key_{self.user_id}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    @task(3)
    def send_message(self):
        # Simulate sending messages
        message_data = {
            "content": f"Load test message {random.randint(1, 1000)}",
            "receiver_id": str(random.randint(1, 1000)),
            "message_type": "text"
        }
        self.client.post(
            "/api/messages/send",
            json=message_data,
            headers=self.headers
        )
    
    @task(2)
    def get_conversation(self):
        # Simulate retrieving conversation history
        other_user = str(random.randint(1, 1000))
        self.client.get(
            f"/api/messages/conversation/{other_user}",
            headers=self.headers
        )
    
    @task(1)
    def update_status(self):
        # Simulate updating message status
        message_id = random.randint(1, 1000)
        status_data = {"status": "read"}
        self.client.put(
            f"/api/messages/{message_id}/status",
            json=status_data,
            headers=self.headers
        )

# To run:
# locust -f locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089 in browser
#
# Configuration recommendations:
# - Start with 10 users, spawn rate 1 user/second
# - Gradually increase to 100 users to test system limits
# - Monitor response times and error rates
# - Watch for database connection pool exhaustion
# - Monitor WebSocket connection limits