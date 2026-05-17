# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

**Backend (Flask API):**
```
python app.py
```
Runs on `http://localhost:5000`. On first run (or if `token.json` is missing/expired), a browser window will open for Google OAuth — this is expected.

**Frontend:**
Open `index.html` directly in a browser. It hardcodes `http://localhost:5000` as the API base. Fonts loaded from Google Fonts (Playfair Display + DM Sans). No build step required.

## Architecture

| File | Role |
|---|---|
| `app.py` | Flask REST API — see routes table below |
| `index.html` | Single-page frontend; vanilla JS, no build step, talks to `app.py` |
| `tasks.json` | Flat JSON array — the only persistence layer |
| `assets/` | Static assets; `screenshot.png` used in README |

**API routes:**

| Method | Route | Description |
|---|---|---|
| GET | `/tasks` | Return all tasks in order |
| POST | `/tasks` | Create task; inserts at index 0 (top of list) |
| PATCH | `/tasks/<index>` | Toggle done/undone |
| PUT | `/tasks/<index>` | Update title, description, and due date |
| PUT | `/tasks/reorder` | Accepts a JSON array of indices; persists new order to `tasks.json` |
| DELETE | `/tasks/<index>` | Remove task |

**Task indexing:** Tasks are identified by their position in the `tasks.json` array. The API routes use `<int:index>` as the identifier, so deleting a task shifts all subsequent indices. The frontend passes the original array index from its in-memory `tasks` array, which can go stale if tasks are modified concurrently.

**Task ordering:** New tasks are prepended (index 0). Active tasks can be manually reordered via drag-and-drop in the UI; the new order is persisted immediately via `PUT /tasks/reorder`.

**Google Calendar:** `app.py` creates Google Calendar **events** (not Google Tasks) when a due date is set. Events use the Calendar API (`google-api-python-client`, scope `https://www.googleapis.com/auth/calendar`), are created on the primary calendar with a 1-hour duration, and the `htmlLink` is stored as `calendar_event_link` on the task. OAuth flow: `credentials.json` → `token.json` (auto-generated on first auth, refreshed automatically). The frontend date picker sends an ISO datetime string which `app.py` parses directly. Timezone is hardcoded to `America/New_York`. Calendar errors are caught and logged but do not block task creation.


## Google OAuth setup

`credentials.json` must exist (Google Cloud Console → OAuth 2.0 Client ID, Desktop app type). `token.json` is auto-generated on first auth and refreshed automatically when expired.
