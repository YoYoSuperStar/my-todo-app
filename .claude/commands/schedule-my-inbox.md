Process the user's Obsidian inbox: turn captured ideas into scheduled tasks in the to-do app, with Google Calendar events, then clear the inbox.

## Steps

1. **Read the inbox** at `C:\Users\joann\Documents\ObsidianVault\Inbox.md`. Extract every non-empty bullet/line under the "To be scheduled" section. Ignore the heading and the instructional preamble.

2. **If the inbox is empty**, tell the user there's nothing to schedule and stop.

3. **Show the user each item and ask for a date + time** (and optional description). Use `AskUserQuestion` if there are 1-4 items; if there are more, ask in a single text message listing all items and prompting for `YYYY-MM-DD HH:MM` for each, plus any items to skip. Default time should be 09:00 if the user gives only a date.

4. **Start the Flask server** if it isn't already running:
   - Probe with `curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/tasks`. If not 200, run `python app.py` in the background and wait for it.

5. **POST each item** to `http://localhost:5000/tasks` with `{"title": "...", "description": "...", "due": "YYYY-MM-DDTHH:MM"}`. This creates the Google Calendar event automatically.

6. **Clear the inbox** — overwrite `Inbox.md` with the original preamble + heading + a single empty bullet, preserving the file structure. Do NOT delete the file.

7. **Stop the Flask server** if you started it in step 4 (don't stop it if the user already had it running).

8. **Report** to the user: list of scheduled tasks with their due dates, and confirm the inbox is cleared.

## Notes

- All times are `Europe/London` (the app's hardcoded timezone).
- If the user said something like "/schedule-my-inbox tomorrow 14:00 for everything", skip the per-item question and apply that date+time to all items.
- If the user wants to skip an item, leave it in the inbox after the sweep (re-add it under the heading).
