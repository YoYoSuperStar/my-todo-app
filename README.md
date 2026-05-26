# My Tasks

A personal task manager with a web UI and REST API — built with Flask and vanilla JS.

## Screenshot

![My Tasks](assets/screenshot.png)

## Features

- **Add, edit, and delete tasks** with an optional description and due date
- **Google Calendar integration** — tasks with a due date create a Calendar event automatically, and edits/deletes sync back to the event
- **Drag-and-drop reordering** — rearrange active tasks by dragging
- **Completion animation** — confetti burst when you tick a task done
- **Analytics** — live donut chart and weekly progress bar
- **Search** — filter tasks instantly from the top bar
- **Responsive** — works on mobile and desktop
- **Obsidian daily note** — `daily_note.py` writes a morning briefing into your Obsidian vault, combining today's tasks and Google Calendar events with cycling categorization

## Running the app

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Set up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Desktop app type)
3. Download and save as `credentials.json` in the project root
4. Enable the **Google Calendar API** for your project

### 3. Start the backend

```
python app.py
```

Runs on `http://localhost:5000`. On first run a browser window will open for Google OAuth — this is expected. The token is saved to `token.json` and refreshed automatically.

Calendar events are created in the `Europe/London` timezone. To change this, edit the `timeZone` field in [app.py](app.py).

### 4. Open the frontend

Open `index.html` directly in your browser.

## Adding tasks via Claude (no UI needed)

You don't have to use the web UI to add tasks. With the Flask backend running, you can just tell Claude Code what's on your plate — by typing or by voice — and Claude will POST them to `/tasks`, which creates the Google Calendar events and persists to `tasks.json` exactly like the UI does. Useful for bulk dictation, e.g. "here's everything I need to get done this week, add them all with due dates."

## Obsidian daily note

`daily_note.py` generates a markdown briefing each morning and drops it into your Obsidian vault (default: `~/Documents/ObsidianVault/Daily/YYYY-MM-DD.md`). It pulls from `tasks.json` and your primary Google Calendar.

**Sections:**

| Section | Contents |
|---|---|
| Tasks due today | Undone tasks due today, merged with non-cycling calendar events, sorted by time |
| Training plan | Personal cycling training (band session, intervals, endurance, recovery, FTP, Zwift, etc.) |
| Live Cycling Events | Pro racing (Giro, Vuelta, Tour de France, UCI, classics) |
| Community rides/events | Group/club/social rides and named series (Porteur, Glorious Gravel, etc.) |
| Overdue | Undone tasks past their due date |
| In-progress ideas | Undone tasks with no due date — longer-term work |

Keyword lists for the cycling sections live at the top of [daily_note.py](daily_note.py) and are intended to be edited as new event names appear.

### Run it manually

```
python daily_note.py
```

### Schedule it (Windows)

A Windows Scheduled Task can run the script automatically each morning:

```powershell
$python = (Get-Command python).Source
$action = New-ScheduledTaskAction -Execute $python -Argument "daily_note.py" -WorkingDirectory "<path-to-this-repo>"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00am
Register-ScheduledTask -TaskName "ClaudePlayground-DailyNote" -Action $action -Trigger $trigger -Force
```

To remove: `Unregister-ScheduledTask -TaskName ClaudePlayground-DailyNote`.

If the note stops appearing in Obsidian, check the task's last run:
```powershell
Get-ScheduledTaskInfo -TaskName ClaudePlayground-DailyNote   # LastRunTime, LastTaskResult (0 = OK)
(Get-ScheduledTask -TaskName ClaudePlayground-DailyNote).Actions  # confirms WorkingDirectory matches the repo path
```
A non-zero `LastTaskResult` (e.g. `2147942667` = directory not found) usually means the repo was moved and the task's `WorkingDirectory` is stale — re-point it with `Set-ScheduledTask`.

## Project structure

| File | Role |
|---|---|
| `app.py` | Flask REST API |
| `index.html` | Single-page web frontend |
| `daily_note.py` | Standalone script that builds the Obsidian daily note |
| `tasks.json` | JSON persistence |
| `credentials.json` | Google OAuth credentials (not committed) |
| `token.json` | Auto-generated OAuth token (not committed) |

## API

| Method | Route | Description |
|---|---|---|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task (creates Calendar event if `due` is set) |
| PUT | `/tasks/<index>` | Update a task (creates / updates / removes the Calendar event to match the new `due`) |
| PATCH | `/tasks/<index>` | Toggle done/undone |
| PUT | `/tasks/reorder` | Persist drag-and-drop order |
| DELETE | `/tasks/<index>` | Delete a task (cancels the linked Calendar event) |
