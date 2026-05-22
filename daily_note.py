import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import dateparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT = Path(__file__).parent
TASKS_FILE = PROJECT / "tasks.json"
TOKEN_FILE = PROJECT / "token.json"
VAULT = Path.home() / "Documents" / "ObsidianVault"
DAILY = VAULT / "Daily"
TZ = ZoneInfo("Europe/London")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
LIVE_CYCLING_KEYWORDS = ("giro", "vuelta", "tour de", "uci", "world championship", "paris-roubaix", "milan-san remo", "classics")
COMMUNITY_KEYWORDS = ("group ride", "neighbourhood", "club ride", "social ride", "community ride", "chaingang", "porteur", "glorious gravel")
TRAINING_KEYWORDS = ("band session", "intervals", "endurance ride", "recovery ride", "long ride", "easy +", "endurance", "recovery", "ftp test", "zwift", "trainerroad")


def event_text(ev):
    return (ev.get("summary", "") + " " + ev.get("description", "")).lower()


def categorize(ev):
    text = event_text(ev)
    if any(k in text for k in LIVE_CYCLING_KEYWORDS):
        return "live"
    if any(k in text for k in COMMUNITY_KEYWORDS):
        return "community"
    if any(k in text for k in TRAINING_KEYWORDS):
        return "training"
    return "other"


def parse_due(s):
    if not s:
        return None
    return dateparser.parse(s)


def fmt_task(task):
    title = task["title"]
    if task.get("due_formatted"):
        return f"- [ ] {title} — _{task['due_formatted']}_"
    return f"- [ ] {title}"


def fmt_event(ev):
    summary = ev.get("summary", "(no title)")
    start = ev.get("start", {})
    if "dateTime" in start:
        dt = datetime.fromisoformat(start["dateTime"]).astimezone(TZ)
        return f"- [ ] {summary} — _{dt.strftime('%H:%M')}_"
    return f"- [ ] {summary} — _all day_"


def event_sort_key(ev):
    start = ev.get("start", {})
    if "dateTime" in start:
        return datetime.fromisoformat(start["dateTime"]).astimezone(TZ)
    return datetime.combine(date.fromisoformat(start["date"]), datetime.min.time(), tzinfo=TZ)


def fetch_calendar_events(today):
    if not TOKEN_FILE.exists():
        return []
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        svc = build("calendar", "v3", credentials=creds)
        start = datetime.combine(today, datetime.min.time(), tzinfo=TZ)
        end = start + timedelta(days=1)
        result = svc.events().list(
            calendarId="primary",
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return result.get("items", [])
    except Exception as e:
        print(f"Calendar fetch error: {e}")
        return []


def section(heading, lines, empty_msg):
    body = lines if lines else [f"_{empty_msg}_"]
    return [f"## {heading}", "", *body, ""]


def main():
    today = date.today()
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))

    due_today_tasks, overdue, ideas = [], [], []
    task_event_ids = set()
    for t in tasks:
        if t.get("calendar_event_id"):
            task_event_ids.add(t["calendar_event_id"])
        if t.get("done"):
            continue
        dt = parse_due(t.get("due"))
        if dt is None:
            ideas.append(t)
        elif dt.date() < today:
            overdue.append(t)
        elif dt.date() == today:
            due_today_tasks.append(t)

    all_events = [e for e in fetch_calendar_events(today) if e.get("id") not in task_event_ids]
    buckets = {"live": [], "community": [], "training": [], "other": []}
    for e in all_events:
        buckets[categorize(e)].append(e)

    today_items = [(event_sort_key(e), fmt_event(e)) for e in buckets["other"]]
    for t in due_today_tasks:
        dt = parse_due(t.get("due"))
        key = dt.astimezone(TZ) if dt and dt.tzinfo else (dt.replace(tzinfo=TZ) if dt else datetime.combine(today, datetime.min.time(), tzinfo=TZ))
        today_items.append((key, fmt_task(t)))
    today_lines = [line for _, line in sorted(today_items, key=lambda x: x[0])]

    DAILY.mkdir(parents=True, exist_ok=True)
    out = DAILY / f"{today.isoformat()}.md"

    def lines_for(bucket):
        return [fmt_event(e) for e in sorted(buckets[bucket], key=event_sort_key)]

    lines = [f"# {today.strftime('%A, %d %B %Y')}", ""]
    lines += section("Tasks due today", today_lines, "Nothing due today.")
    lines += section("Training plan", lines_for("training"), "No training today.")
    lines += section("Live Cycling Events", lines_for("live"), "No live events today.")
    lines += section("Community rides/events", lines_for("community"), "No community rides today.")
    lines += section("Overdue", [fmt_task(t) for t in overdue], "Nothing overdue.")
    lines += section("In-progress ideas", [fmt_task(t) for t in ideas], "No ideas captured.")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({len(all_events)} calendar events + {len(due_today_tasks)} task(s) due today)")


if __name__ == "__main__":
    main()
