import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import threading

# There's only one JSON file for all users, so we need to ensure thread safety.
# This lock will prevent multiple threads from writing to the file at the same time.
# If you have more than a few users, consider using a database instead. This is a simple solution
# and works for me and my friends.
file_lock = threading.Lock()


class Filter:
    """
    title: Quota Lock
    author: Eric Stein
    version: 1.0.0
    required_open_webui_version: n/a
    description: Sets a monthly request limit for each user.
    """

    # Valves
    class Valves(BaseModel):
        MONTHLY_REQUEST_LIMIT: int = Field(
            default=100,
            description="The maximum number of requests a user can make per month.",
        )
        QUOTA_DATA_FILE: str = Field(
            default="data/quota_data.json",
            description="Path to the JSON file for storing user quota usage.",
        )

    def __init__(self):
        self.valves = self.Valves()
        print(
            f"Quota Filter initialized. Limit: {self.valves.MONTHLY_REQUEST_LIMIT}, Data file: {self.valves.QUOTA_DATA_FILE}"
        )

        data_dir = os.path.dirname(self.valves.QUOTA_DATA_FILE)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_quota_data(self) -> dict:
        """Lädt die Nutzungsdaten aus der JSON-Datei."""
        with file_lock:
            if not os.path.exists(self.valves.QUOTA_DATA_FILE):
                return {}
            try:
                with open(self.valves.QUOTA_DATA_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}

    def _save_quota_data(self, data: dict):
        """Speichert die Nutzungsdaten in der JSON-Datei."""
        with file_lock:
            with open(self.valves.QUOTA_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        Diese Funktion wird vor jeder Anfrage an das LLM ausgeführt.
        Sie prüft das Kontingent des Nutzers.
        """
        if not __user__ or not __user__.get("id"):
            # If no user can be identified, the request is denied.
            # This adds extra security to prevent unauthorized access.
            raise Exception("User could not be identified for quota check.")

        user_id = str(__user__["id"])
        quota_data = self._load_quota_data()

        current_month = datetime.now().strftime("%Y-%m")

        if user_id not in quota_data:
            quota_data[user_id] = {}

        if current_month not in quota_data[user_id]:
            quota_data[user_id][current_month] = {"count": 0}

        usage_count = quota_data[user_id][current_month]["count"]

        # Check quota
        if usage_count >= self.valves.MONTHLY_REQUEST_LIMIT:
            raise Exception(
                f"Monthly quota of {self.valves.MONTHLY_REQUEST_LIMIT} requests exceeded. Please try again next month."
            )
        else:
            # If the quota is not exceeded, increment the count for the current month
            quota_data[user_id][current_month]["count"] += 1
            self._save_quota_data(quota_data)

            # Forward the request
            print(
                f"User {user_id} request {usage_count + 1}/{self.valves.MONTHLY_REQUEST_LIMIT} for month {current_month} approved."
            )
            return body

    # empty placeholder functions
    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body

    def stream(self, event: dict) -> dict:
        return event
