import argparse
import calendar
import json
import math
import shutil
import sqlite3
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COURSE_PROGRESS = DATA / "course_progress.json"
COURSE_HISTORY = DATA / "course_history.json"
READING_LOG = DATA / "reading_log.json"
READING_PROGRESS = DATA / "reading_progress.json"
READING_SESSION = DATA / "reading_session.json"
PDF_PROGRESS = DATA / "pdf_progress.json"
ACTIVITY_LOG = DATA / "activity_log.json"
OUTPUT = DATA / "progress.json"
COURSE_DURATIONS = Path(r"D:\WOK\POKESTOP\french_a1\data\video_durations.json")
ANKI_ROOT = Path.home() / "AppData" / "Roaming" / "Anki2"
COURSE_LABELS = {"phonetics": "A0", "a1": "A1", "a2": "A2", "b1": "B1", "b2": "B2"}


def month_plan(completed, target, history_values, unit):
    today = datetime.now().date()
    month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    days_remaining = (month_end - today).days + 1
    completed = int(completed or 0)
    target = int(target or 0)
    remaining = max(0, target - completed)
    recommended = math.ceil(remaining / days_remaining) if remaining else 0
    yesterday_key = (today - timedelta(days=1)).isoformat()
    yesterday_done = int(history_values.get(yesterday_key, 0) or 0)
    eta_days = math.ceil(remaining / yesterday_done) if yesterday_done > 0 and remaining else 0
    eta_date = (today + timedelta(days=eta_days)).isoformat() if eta_days else None
    return {
        "unit": unit,
        "target": target,
        "completed": completed,
        "remaining": remaining,
        "percent": round(completed / target * 100, 2) if target else 0,
        "daysRemaining": days_remaining,
        "deadline": month_end.isoformat(),
        "recommendedToday": recommended,
        "yesterdayDone": yesterday_done,
        "etaDays": eta_days,
        "etaDate": eta_date,
    }


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def local_date_from_ms(value):
    return datetime.fromtimestamp(value / 1000).date().isoformat()


def find_anki_collection():
    candidates = list(ANKI_ROOT.glob("*/collection.anki2"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def collect_anki(days=30):
    result = {
        "today": {"reviews": 0, "new": 0, "minutes": 0},
        "total": {"cards": 0, "mature": 0, "learned": 0, "newRemaining": 0, "percent": 0},
        "streak": 0,
        "history": [],
        "decks": [],
    }
    source = find_anki_collection()
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    daily = defaultdict(lambda: {"reviews": 0, "new": 0, "minutes": 0})
    if source:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "collection.anki2"
            shutil.copy2(source, copy)
            db = sqlite3.connect(copy)
            db.create_collation("unicase", lambda a, b: (a.casefold() > b.casefold()) - (a.casefold() < b.casefold()))
            try:
                result["total"]["cards"] = db.execute("select count(*) from cards").fetchone()[0]
                result["total"]["mature"] = db.execute("select count(*) from cards where ivl >= 21").fetchone()[0]
                result["total"]["learned"] = db.execute("select count(*) from cards where type != 0 or reps > 0").fetchone()[0]
                result["total"]["newRemaining"] = db.execute("select count(*) from cards where type = 0 and reps = 0").fetchone()[0]
                result["total"]["percent"] = round(
                    result["total"]["learned"] / result["total"]["cards"] * 100,
                    2,
                ) if result["total"]["cards"] else 0
                for did, name, total, learned, mature, new_remaining in db.execute(
                    """
                    select d.id, d.name, count(c.id),
                      sum(case when c.type != 0 or c.reps > 0 then 1 else 0 end),
                      sum(case when c.ivl >= 21 then 1 else 0 end),
                      sum(case when c.type = 0 and c.reps = 0 then 1 else 0 end)
                    from decks d join cards c on c.did=d.id
                    group by d.id, d.name
                    having count(c.id) > 0
                    order by count(c.id) desc
                    limit 20
                    """
                ):
                    result["decks"].append({
                        "id": did,
                        "name": str(name).replace("\x1f", "::"),
                        "cards": total or 0,
                        "learned": learned or 0,
                        "mature": mature or 0,
                        "newRemaining": new_remaining or 0,
                        "percent": round((learned or 0) / total * 100, 2) if total else 0,
                    })
                start_ms = int(datetime.combine(start, datetime.min.time()).timestamp() * 1000)
                for stamp, count, elapsed in db.execute(
                    "select id, count(*), sum(time) from revlog where id >= ? group by date(id / 1000, 'unixepoch', 'localtime')",
                    (start_ms,),
                ):
                    key = local_date_from_ms(stamp)
                    daily[key]["reviews"] = count
                    daily[key]["minutes"] = round((elapsed or 0) / 60000, 1)
                for stamp, count in db.execute(
                    "select min(id), count(*) from revlog group by cid having min(id) >= ?",
                    (start_ms,),
                ):
                    daily[local_date_from_ms(stamp)]["new"] += count
            finally:
                db.close()
    for offset in range(days):
        key = (start + timedelta(days=offset)).isoformat()
        result["history"].append({"date": key, **daily[key]})
    result["today"] = daily[today.isoformat()]
    result["today"]["activityComplete"] = bool(
        result["today"]["reviews"] or result["today"]["new"] or result["today"]["minutes"]
    )
    result["today"]["goalPercent"] = 100 if result["today"]["activityComplete"] else 0
    cursor = today
    while daily[cursor.isoformat()]["reviews"] > 0:
        result["streak"] += 1
        cursor -= timedelta(days=1)
    return result


def collect_course(days=365):
    synced = read_json(COURSE_PROGRESS, {})
    if synced.get("courses"):
        for course in synced["courses"]:
            course["label"] = COURSE_LABELS.get(course.get("id"), course.get("label", "Course"))
        history = read_json(COURSE_HISTORY, {"entries": []})
        pdf = read_json(PDF_PROGRESS, {"documents": {}, "daily": {}})
        today = datetime.now().date().isoformat()
        row = next((x for x in history.get("entries", []) if x.get("date") == today), {})
        total_watched = float(synced.get("total", {}).get("watchedSeconds", 0) or 0)
        baseline = float(row.get("baselineSeconds", total_watched) or 0)
        inferred_today = max(0, total_watched - baseline)
        watched_today = max(0, float(row.get("dailySeconds", 0) or 0), inferred_today)
        video_minutes = round(watched_today / 60, 1)
        pdf_minutes = round(float(pdf.get("daily", {}).get(today, 0) or 0) / 60, 1)
        minutes = round(video_minutes + pdf_minutes, 1)
        saved_docs = pdf.get("documents", {})
        docs = [
            saved_docs.get("a1-grammar", {"id": "a1-grammar", "title": "A1 语法讲义", "currentPage": 0, "totalPages": 88, "seconds": 0}),
        ]
        pdf_pages = sum(int(x.get("currentPage", 0) or 0) for x in docs)
        pdf_total_pages = sum(int(x.get("totalPages", 0) or 0) for x in docs)
        pdf_percent = round(pdf_pages / pdf_total_pages * 100, 2) if pdf_total_pages else 0
        pdf_daily_pages = {k: int(v or 0) for k, v in pdf.get("dailyPages", {}).items()}
        synced["today"] = {
            "minutes": minutes,
            "videoMinutes": video_minutes,
            "pdfMinutes": pdf_minutes,
            "activityComplete": minutes > 0,
            "goalPercent": 100 if minutes > 0 else 0,
        }
        synced["pdf"] = {
            "pages": pdf_pages,
            "totalPages": pdf_total_pages,
            "percent": pdf_percent,
            "documents": docs,
            "todayPages": int(pdf_daily_pages.get(today, 0) or 0),
            "month": month_plan(pdf_pages, pdf_total_pages, pdf_daily_pages, "pages"),
        }
        start = datetime.now().date() - timedelta(days=days - 1)
        daily = {x.get("date"): x for x in history.get("entries", [])}
        synced["history"] = []
        for offset in range(days):
            key = (start + timedelta(days=offset)).isoformat()
            item = daily.get(key, {})
            video_minutes = round(max(0, float(item.get("dailySeconds", 0) or 0)) / 60, 1)
            pdf_minutes = round(float(pdf.get("daily", {}).get(key, 0) or 0) / 60, 1)
            minutes = round(video_minutes + pdf_minutes, 1)
            synced["history"].append({
                "date": key,
                "minutes": minutes,
                "videoMinutes": video_minutes,
                "pdfMinutes": pdf_minutes,
                "activityComplete": minutes > 0,
                "goalPercent": 100 if minutes > 0 else 0,
            })
        return synced
    durations = read_json(COURSE_DURATIONS, {})
    totals = defaultdict(float)
    for key, seconds in durations.items():
        totals[key.split("/", 1)[0]] += float(seconds or 0)
    courses = [
        {
            "id": key,
            "label": COURSE_LABELS.get(key, key.upper()),
            "watchedSeconds": 0,
            "durationSeconds": round(total, 2),
            "percent": 0,
        }
        for key, total in totals.items()
    ]
    return {
        "updatedAt": None,
        "lastLesson": None,
        "courses": courses,
        "total": {"watchedSeconds": 0, "durationSeconds": round(sum(totals.values()), 2), "percent": 0},
        "today": {"minutes": 0, "videoMinutes": 0, "pdfMinutes": 0, "activityComplete": False, "goalPercent": 0},
        "pdf": {"pages": 0, "totalPages": 88, "percent": 0, "documents": [
            {"id": "a1-grammar", "title": "A1 语法讲义", "currentPage": 0, "totalPages": 88, "seconds": 0},
        ]},
    }


def collect_reading(days=30):
    raw = read_json(READING_LOG, {"entries": []})
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    daily = defaultdict(lambda: {"articles": 0, "minutes": 0})
    for entry in raw.get("entries", []):
        key = entry.get("date", "")
        if key < start.isoformat() or not str(entry.get("source", "")).startswith("lingua"):
            continue
        daily[key]["articles"] += int(entry.get("sets", 0) or 0)
        daily[key]["minutes"] += float(entry.get("minutes", 0) or 0)
    history = []
    for offset in range(days):
        key = (start + timedelta(days=offset)).isoformat()
        row = {"date": key, **daily[key]}
        row["articles"] = max(0, int(row["articles"]))
        row["goalPercent"] = round(min(1, row["articles"] / 3) * 100, 2)
        history.append(row)
    today_row = history[-1]
    today_row["target"] = 3
    today_row["activityComplete"] = today_row["articles"] >= 3
    return {
        "today": today_row,
        "history": history,
        "source": "https://lingua.com/french/reading/",
    }


def collect_activity(days=365):
    raw = read_json(ACTIVITY_LOG, {"days": {}, "lastContext": "grammar"})
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    history = []
    for offset in range(days):
        key = (start + timedelta(days=offset)).isoformat()
        row = raw.get("days", {}).get(key, {})
        reading = round(float(row.get("reading", 0) or 0) / 60, 1)
        grammar = round(float(row.get("grammar", 0) or 0) / 60, 1)
        verb = round(float(row.get("verb", 0) or 0) / 60, 1)
        history.append({
            "date": key,
            "readingMinutes": reading,
            "grammarMinutes": grammar,
            "verbMinutes": verb,
            "totalMinutes": round(reading + grammar + verb, 1),
            "warnings": row.get("warnings", []),
        })
    return {
        "today": history[-1],
        "history": history,
        "lastContext": raw.get("lastContext", "grammar"),
    }


def main():
    parser = argparse.ArgumentParser(description="Collect local study stats for the public dashboard.")
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()
    anki = collect_anki(args.days)
    course = collect_course(args.days)
    reading = collect_reading(args.days)
    activity = collect_activity(args.days)
    fallback_focus = anki["today"]["minutes"] + reading["today"]["minutes"] + course["today"]["minutes"]
    focus = round(activity["today"]["totalMinutes"] or fallback_focus)
    payload = {
        "updatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": {"date": datetime.now().date().isoformat(), "focusMinutes": focus},
        "anki": anki,
        "course": course,
        "reading": reading,
        "activity": activity,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {OUTPUT}")


if __name__ == "__main__":
    main()
