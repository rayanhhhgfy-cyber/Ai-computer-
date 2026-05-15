import requests
import time
import json
from datetime import datetime

class SupabaseBridge:
    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def post_log(self, message):
        """Sends a log message to the Supabase 'logs' table."""
        endpoint = f"{self.url}/rest/v1/logs"
        data = {"message": message}
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            return response.status_code == 201
        except Exception as e:
            print(f"Remote Log Error: {e}")
            return False

    def get_latest_command(self):
        """Fetches the latest 'pending' command from the 'commands' table."""
        endpoint = f"{self.url}/rest/v1/commands?status=eq.pending&order=created_at.desc&limit=1"
        try:
            response = requests.get(endpoint, headers=self.headers)
            if response.status_code == 200:
                commands = response.json()
                if commands:
                    return commands[0]
            return None
        except Exception as e:
            print(f"Remote Command Fetch Error: {e}")
            return None

    def update_command_status(self, command_id, status="completed"):
        """Updates the status of a command."""
        endpoint = f"{self.url}/rest/v1/commands?id=eq.{command_id}"
        data = {"status": status}
        try:
            response = requests.patch(endpoint, headers=self.headers, json=data)
            return response.status_code == 204 or response.status_code == 200
        except Exception as e:
            print(f"Remote Command Update Error: {e}")
            return False

    def send_screenshot(self, base64_image):
        """Sends the latest screenshot to a 'state' table to show on the iPhone."""
        endpoint = f"{self.url}/rest/v1/state"
        # We use an upsert (id=1) for the current state
        # ISO format for Supabase compatibility
        now_iso = datetime.utcnow().isoformat()
        data = {"id": 1, "last_screenshot": base64_image, "updated_at": now_iso}
        headers = self.headers.copy()
        headers["Prefer"] = "resolution=merge-duplicates"
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            return response.status_code in [200, 201, 204]
        except Exception as e:
            print(f"Remote Screenshot Error: {e}")
            return False
