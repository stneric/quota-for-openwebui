# Quota Lock - Open WebUI Plugin

A simple plugin for [Open WebUI](https://github.com/open-webui/open-webui) that sets a monthly request limit for each user. It consists of two parts: a **filter** to enforce the quota and an **action** for users to check their current usage.

This plugin is ideal for server administrators who share an Open WebUI instance with friends, family, or a small team and want to ensure fair usage or manage costs associated with API-based models.

### Note:
This plugin is not suitable for large-scale use! It uses a single JSON file to manage quotas. For a scalable implementation, consider using a database.

---

## Features

This plugin provides two key functions that work together:

#### 1. Quota Lock (Filter)

-   **Per-User Quotas**: Each user's request count is tracked individually.
-   **Monthly Reset**: Quotas automatically reset at the beginning of each calendar month.
-   **Configurable Limit**: Easily set the maximum number of requests allowed per month.
-   **Persistent Storage**: User data is saved to a JSON file, so usage counts are remembered after restarts.
-   **Lightweight**: No external database required. It's a simple, file-based solution.
-   **Secure**: Denies requests if a user cannot be identified, preventing unauthenticated use from bypassing the quota.

#### 2. Show My Quota (Action)

-   **User-Facing Button**: Adds a function button that allows users to check their quota at any time.
-   **Displays Current Usage**: Shows the user how many requests they've used, how many are remaining, and what their total monthly limit is.

---

## Installation

You need to install two separate components: the filter and the action.

1.  Navigate to the Admin Panel in your Open WebUI instance.
2.  Go to the **Functions** section.

#### To Install the "Quota Lock" Filter:
1.  Click add.
2.  Paste the code from your first file (`quota-lock.py`) into the editor.
3.  Save the filter.
4.  **Important**: Configure the filter to be **enabled globally** so it applies to all users and models.

#### To Install the "Show My Quota" Action:
1.  Click add.
2.  Paste the code from your new file (`check-quota.py` or similar) into the editor.
3.  Save the action. The button will now be available to users. Also needs to be **enabled globally**.

---

## How to Use & Configure

Once installed and enabled globally, the filter works automatically. It gives every user a default of **100 requests per month**. When a user exceeds this limit, they will receive an error message and be blocked from making further requests until the next month.

Users can click the "Show My Quota" button at any time to see a message like this in their chat:

> 📊 **Your monthly usage**
>
> ▪️ **Used:** 9
> ▪️ **Remaining:** 91
> ▪️ **Limit:** 100

### Changing the Request Limit & Configuration

Both the filter and the action have settings (Valves) that you can configure directly in the Open WebUI Admin Panel.

1.  In the Admin Panel, go to **Tools**.
2.  Find "Quota Lock" (the filter) and "Show My Quota" (the action).
3.  Click the **cog icon** to open the valves for each one.

You will see these two settings:
-   `MONTHLY_REQUEST_LIMIT`: The maximum number of requests a user can make per month.
-   `QUOTA_DATA_FILE`: The path to the JSON file for storing usage data.

> **⚠️ CRITICAL CONFIGURATION NOTE**
>
> For the plugin to work correctly, the values for `MONTHLY_REQUEST_LIMIT` and `QUOTA_DATA_FILE` **must be identical** for both the **Quota Lock (Filter)** and the **Show My Quota (Action)**. If they are different, the action will show incorrect quota information to the user.

---

### > ⚠️ Important Note for Docker Users

This plugin stores usage data in a file to ensure it persists between server restarts. If you are running Open WebUI in a Docker container, **you must use a volume to persist the data directory.**

The standard `docker run` or `docker-compose.yml` provided by the Open WebUI project should already do this by mapping a local folder to `/app/backend/data` inside the container.

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

#### Quota Lock (Filter)
The filter's logic is contained within the `inlet` function, which runs *before* every request is sent to a language model.
1.  It intercepts the incoming request and identifies the user by their unique ID.
2.  It loads the usage data from the `quota_data.json` file.
3.  It checks the current user's request `count` for the current month (e.g., "2025-06").
4.  If the user's count is less than `MONTHLY_REQUEST_LIMIT`, it increments the count, saves the data, and allows the request to proceed.
5.  If the count has reached the limit, it raises an exception, blocking the request and showing an error to the user.

#### Show My Quota (Action)
The action runs when a user clicks the corresponding button.
1. It identifies the currently logged-in user.
2. It reads the *same* `quota_data.json` file.
3. It retrieves the user's current `count`, calculates the remaining requests based on the `MONTHLY_REQUEST_LIMIT`, and formats a user-friendly message.
4. It sends this message directly back to the user's chat interface.

### Data Storage

The plugin uses a `quota_data.json` file stored in the location specified by the `QUOTA_DATA_FILE` valve (defaulting to `data/quota_data.json` relative to the `backend` directory). The data is stored in a simple JSON format, mapping user IDs to their monthly usage.

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
            "count": 100
        }
    }
}
```
-   **`3ca797...`**: The unique ID of a user.
-   **`2025-06`**: The year and month the count applies to.
-   **`count`**: The number of requests made by that user in that month.

---

*Author: Eric Stein*
*Version: 2.0.0*