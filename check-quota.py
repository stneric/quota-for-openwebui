from pydantic import BaseModel, Field
from typing import Optional, Any
import os
import json
from datetime import datetime
import traceback


class Action:
    """
    title: Show My Quota
    author: Eric Stein
    version: 1.0
    description: Displays the current user's monthly quota.
    requires_user: true
    """

    class Valves(BaseModel):
        MONTHLY_REQUEST_LIMIT: int = Field(default=100)
        QUOTA_DATA_FILE: str = Field(default="data/quota_data.json")

    def __init__(self):
        self.valves = self.Valves()

    async def action(
        self,
        body: dict,
        *,
        __user__: Optional[Any] = None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> None:
        try:
            user_dict = None
            if (
                isinstance(__user__, tuple)
                and len(__user__) > 0
                and isinstance(__user__[0], dict)
            ):
                user_dict = __user__[0]
            elif isinstance(__user__, dict):
                user_dict = __user__ 

            if not user_dict or not user_dict.get("id"):
                error_msg = f"Error: Userdata could not be parsed. Recieved: {__user__}."
                print(
                )
                if __event_emitter__:
                    await __event_emitter__(
                        {"type": "message", "data": {"content": error_msg}}
                    )
                return

            user_id = str(user_dict["id"])

            limit = self.valves.MONTHLY_REQUEST_LIMIT
            file_path = self.valves.QUOTA_DATA_FILE

            quota_data = {}
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                    if content:
                        quota_data = json.loads(content)

            current_month = datetime.now().strftime("%Y-%m")
            usage_count = (
                quota_data.get(user_id, {}).get(current_month, {}).get("count", 0)
            )
            remaining = limit - usage_count

            response_message = (
                f" "
                f"📊 **Your montly usage**\n\n"
                f"▪️ **Used:** {usage_count}\n"
                f"▪️ **Remaining:** {max(0, remaining)}\n"
                f"▪️ **Limit:** {limit}"
            )

            if __event_emitter__:
                await __event_emitter__(
                    {"type": "message", "data": {"content": response_message}}
                )

        except Exception as e:
            error_msg = f"Ein interner Fehler ist aufgetreten: {e}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "message", "data": {"content": error_msg}}
                )
        finally:
            print("Checked quota for user:", user_id)
