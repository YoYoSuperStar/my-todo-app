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
| `daily_note.py` | Standalone script that generates the Obsidian daily note (see "Obsidian daily note" below) |
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

**Google Calendar:** `app.py` creates Google Calendar **events** (not Google Tasks) when a due date is set. Events use the Calendar API (`google-api-python-client`, scope `https://www.googleapis.com/auth/calendar`), are created on the primary calendar with a 1-hour duration, and the `htmlLink` is stored as `calendar_event_link` on the task. OAuth flow: `credentials.json` → `token.json` (auto-generated on first auth, refreshed automatically). The frontend date picker sends an ISO datetime string which `app.py` parses directly. Timezone is hardcoded to `Europe/London`. Calendar errors are caught and logged but do not block task operations.

**Calendar sync (POST / PUT / DELETE):** all three mutating routes sync to Google Calendar via helpers in `app.py` — `create_calendar_event`, `update_calendar_event`, `delete_calendar_event`. PUT diff logic: gaining a due date creates an event; changing date/title/description with an existing event updates it; clearing the due date cancels the event. DELETE cancels the linked event before removing the task.


## Google OAuth setup

`credentials.json` must exist (Google Cloud Console → OAuth 2.0 Client ID, Desktop app type). `token.json` is auto-generated on first auth and refreshed automatically when expired.

## Obsidian daily note

`daily_note.py` is a standalone script (no Flask dependency) that writes a markdown daily note to `~/Documents/ObsidianVault/Daily/YYYY-MM-DD.md`. Reads `tasks.json` and the user's primary Google Calendar (reusing `token.json`).

**Sections written:**
- **Tasks due today** — undone tasks with `due` matching today's date, merged with non-cycling calendar events, sorted by time
- **Training plan** — calendar events matching personal training keywords (band session, intervals, endurance ride, recovery, FTP test, Zwift, TrainerRoad, etc.)
- **Live Cycling Events** — pro racing keywords (Giro, Vuelta, Tour de, UCI, world championship, classics, Paris-Roubaix, Milan-San Remo)
- **Community rides/events** — group/club/social ride keywords plus named series (Porteur, Glorious Gravel, etc.)
- **Overdue** — undone tasks with `due` before today
- **In-progress ideas** — undone tasks with no `due` date

Categorization order is live → community → training (first match wins). Keyword lists live at the top of `daily_note.py` and are intended to be edited as new event names appear.

**Dedup:** events whose `id` matches a `calendar_event_id` on a task in `tasks.json` are dropped from the calendar pull so they only appear once (as the task).

**Scheduling:** a Windows Scheduled Task named `ClaudePlayground-DailyNote` runs `pythonw.exe daily_note.py` daily at 09:00. Use **`pythonw.exe`** (not `python.exe`) so the task runs silently with no console window — a visible console window can be closed by mistake, which kills the script and leaves the day's note ungenerated (manifests as `LastTaskResult: 3221225786` / `0xC000013A` = Ctrl+C/terminated).

The name retains the project's previous folder name (`Claude Playground`) — the project now lives at `C:\Users\joann\repos\to-do app` and the task's `WorkingDirectory` must point there, not the old path. Manage with:
```
Get-ScheduledTask -TaskName ClaudePlayground-DailyNote
(Get-ScheduledTask -TaskName ClaudePlayground-DailyNote).Actions  # check Execute + WorkingDirectory
Get-ScheduledTaskInfo -TaskName ClaudePlayground-DailyNote        # LastRunTime + LastTaskResult
Unregister-ScheduledTask -TaskName ClaudePlayground-DailyNote
```
If the project is ever moved or renamed, re-point the task with `Set-ScheduledTask -Action (New-ScheduledTaskAction -Execute <pythonw> -Argument "daily_note.py" -WorkingDirectory <new-path>)`.

Timezone is `Europe/London`, matching `app.py`.

## Obsidian inbox

`~/Documents/ObsidianVault/Inbox.md` is a hand-edited capture file for ideas the user wants to schedule later. It is **never** touched by `daily_note.py` — only by the user (during the day) and by the `/schedule-my-inbox` slash command (when invoked).

The `/schedule-my-inbox` command (`.claude/commands/schedule-my-inbox.md`) reads the "To be scheduled" section of `Inbox.md`, prompts for due dates, POSTs each item to `/tasks` (which creates the Calendar event), and clears the inbox back to its empty state. If the user mentions adding things to capture during the day, point them at `Inbox.md` rather than editing daily notes (which get overwritten on the next 09:00 run).
