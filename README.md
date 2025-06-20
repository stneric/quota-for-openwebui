# Quota Lock - Open WebUI Plugin

A simple but effective filter plugin for [Open WebUI](https://github.com/open-webui/open-webui) that sets a monthly request limit for each user.

This plugin is ideal for server administrators who share an Open WebUI instance with friends, family, or a small team and want to ensure fair usage or manage costs associated with API-based models.

## Note:
This plugin is not suitable for large scale use! It uses a <ul>single</ul> JSON file to manage quotas.
For a scalable implementation, either use a DB or (a bit hacky) multiple JSON files named like the user ids.
---

## Features

-   **Per-User Quotas**: Each user's request count is tracked individually.
-   **Monthly Reset**: Quotas automatically reset at the beginning of each calendar month.
-   **Configurable Limit**: Easily set the maximum number of requests allowed per month.
-   **Persistent Storage**: User data is saved to a JSON file, so usage counts are remembered after restarts.
-   **Lightweight**: No external database required. It's a simple, file-based solution.
-   **Secure**: Denies requests if a user cannot be identified, preventing unauthenticated use from bypassing the quota.

## Installation

1.  Navigate to the admin panel in open webui
2.  -> Functions -> Add
3.  Paste the code from `quota-lock.py` into the editor
4.  Save and configure
5.  Configure so it's used globally 

## How to Use & Configure

The plugin works automatically once installed. By default, it gives every user **100 requests per month**. When a user exceeds this limit, they will receive an error message and be blocked from making further requests until the next month.

### Changing the Request Limit

You can easily change the monthly limit by editing the valves (cog-button in openwebui) or by changing the `filter.py` file.

1.  Open `open-webui/backend/data/filters/quota_lock/filter.py`.
2.  Find the `Valves` class inside the `Filter` class.
3.  Change the `default` value for `MONTHLY_REQUEST_LIMIT`.

```python
# ... (inside the Filter class)

    # Valves
    class Valves(BaseModel):
        MONTHLY_REQUEST_LIMIT: int = Field(
            default=200,  # <-- CHANGE THIS VALUE
            description="The maximum number of requests a user can make per month.",
        )
# ...
```

4.  Save the file.

There's no need to restart openwebui but if there are any issues, give it a try.

---

### > ⚠️ Important Note for Docker Users

This plugin stores usage data in a file to ensure it persists between server restarts. If you are running Open WebUI in a Docker container, **you must use a volume to persist the data directory.**

The standard `docker run` or `docker-compose.yml` provided by the Open WebUI project already does this by mapping a local folder to `/app/backend/data` inside the container as far as I'm aware.

**Example `docker-compose.yml` snippet:**

```yaml
services:
  open-webui:
    # ...
    volumes:
      - open-webui:/app/backend/data
# ...
volumes:
  open-webui: {}
```

As long as you have this volume mapping in place, your plugin and its quota data will be safe. If you run a container without this persistent volume, **all quota data will be lost** every time the container is stopped or recreated.

---

## How It Works

The plugin's logic is contained within the `inlet` function, which runs before every request is sent to a language model.

1.  It intercepts the incoming request and identifies the user by their unique ID.
2.  It loads the usage data from the `quota_data.json` file.
3.  It checks the current user's request `count` for the current month (e.g., "2025-06").
4.  If the user's count is less than `MONTHLY_REQUEST_LIMIT`, it increments the count, saves the data back to the file, and allows the request to proceed.
5.  If the count has reached the limit, it raises an exception, blocking the request and showing an error to the user.

### Data Storage

The plugin will create a `data` folder and a `quota_data.json` file inside its directory (`backend/data/filters/quota_lock/`). The data is stored in a simple JSON format, mapping user IDs to their monthly usage.

**Example `quota_data.json`:**

```json
{
    "3ca79777-2ef1-46cc-a07e-31cdd54dbf4d": {
        "2025-06": {
            "count": 9
        }
    },
    "836805d6-3dae-41ea-905b-813e7dbc46f3": {
        "2025-06": {
            "count": 10
        }
    }
}
```

-   **`3ca797...`**: The unique ID of a user.
-   **`2025-06`**: The year and month the count applies to.
-   **`count`**: The number of requests made by that user in that month.

---
*Author: Eric Stein*
*Version: 1.0.0*