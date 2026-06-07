import argparse
import json
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
OUTPUT = DATA / "progress.json"
COURSE_DURATIONS = Path(r"D:\WOK\POKESTOP\french_a1\data\video_durations.json")
ANKI_ROOT = Path.home() / "AppData" / "Roaming" / "Anki2"
COURSE_LABELS = {"phonetics": "A0", "a1": "A1", "a2": "A2", "b1": "B1", "b2": "B2"}


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
        "total": {"cards": 0, "mature": 0},
        "streak": 0,
        "history": [],
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
            try:
                result["total"]["cards"] = db.execute("select count(*) from cards").fetchone()[0]
                result["total"]["mature"] = db.execute("select count(*) from cards where ivl >= 21").fetchone()[0]
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
        today = datetime.now().date().isoformat()
        row = next((x for x in history.get("entries", []) if x.get("date") == today), {})
        total_watched = float(synced.get("total", {}).get("watchedSeconds", 0) or 0)
        baseline = float(row.get("baselineSeconds", total_watched) or 0)
        inferred_today = max(0, total_watched - baseline)
        watched_today = max(0, float(row.get("dailySeconds", 0) or 0), inferred_today)
        minutes = round(watched_today / 60, 1)
        synced["today"] = {
            "minutes": minutes,
            "goalMinutes": 60,
            "goalPercent": round(min(1, minutes / 60) * 100, 2),
        }
        start = datetime.now().date() - timedelta(days=days - 1)
        daily = {x.get("date"): x for x in history.get("entries", [])}
        synced["history"] = []
        for offset in range(days):
            key = (start + timedelta(days=offset)).isoformat()
            item = daily.get(key, {})
            minutes = round(max(0, float(item.get("dailySeconds", 0) or 0)) / 60, 1)
            synced["history"].append({
                "date": key,
                "minutes": minutes,
                "goalPercent": round(min(1, minutes / 60) * 100, 2),
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
        "today": {"minutes": 0, "goalMinutes": 60, "goalPercent": 0},
    }


def collect_reading(days=30):
    raw = read_json(READING_LOG, {"entries": []})
    automatic = read_json(READING_PROGRESS, {"entries": []})
    session = read_json(READING_SESSION, {"startedAt": None, "baselines": {}})
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    daily = defaultdict(lambda: {"sets": 0, "questions": 0, "correct": 0, "minutes": 0})
    for entry in raw.get("entries", []):
        key = entry.get("date", "")
        if key < start.isoformat():
            continue
        for field in ("sets", "questions", "correct", "minutes"):
            daily[key][field] += float(entry.get(field, 0) or 0)
    tests = defaultdict(list)
    previous_by_test = {}
    entries = sorted(automatic.get("entries", []), key=lambda row: str(row.get("capturedAt", "")))
    session_day = str(session.get("startedAt") or "")[:10]
    for entry in entries:
        key = entry.get("date", "")
        if key < start.isoformat():
            continue
        test = str(entry.get("test", ""))
        current = {
            "answered": int(entry.get("answered", 0) or 0),
            "correct": int(entry.get("correct", 0) or 0),
            "seconds": int(entry.get("seconds", 0) or 0),
        }
        baseline = previous_by_test.get(test, {"answered": 0, "correct": 0, "seconds": 0})
        if key == session_day:
            baseline = session.get("baselines", {}).get(test, baseline)
        answered = current["answered"] - int(baseline.get("answered", 0) or 0)
        correct = current["correct"] - int(baseline.get("correct", 0) or 0)
        seconds = current["seconds"] - int(baseline.get("seconds", 0) or 0)
        if answered < 0:
            answered = current["answered"]
        if correct < 0:
            correct = current["correct"]
        if seconds < 0:
            seconds = current["seconds"]
        if answered == 0:
            seconds = 0
        daily[key]["sets"] += answered / 39
        daily[key]["questions"] += answered
        daily[key]["correct"] += correct
        daily[key]["minutes"] += round(seconds / 60, 1)
        tests[key].append({
            "test": test,
            "answered": answered,
            "correct": correct,
            "total": 39,
        })
        previous_by_test[test] = current
    history = []
    for offset in range(days):
        key = (start + timedelta(days=offset)).isoformat()
        row = {"date": key, **daily[key], "tests": tests[key]}
        row["accuracy"] = round(row["correct"] / row["questions"] * 100, 2) if row["questions"] else 0
        row["goalPercent"] = round(min(1, row["questions"] / 39) * 100, 2)
        history.append(row)
    today_row = history[-1]
    return {"today": today_row, "history": history}


def main():
    parser = argparse.ArgumentParser(description="Collect local study stats for the public dashboard.")
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()
    anki = collect_anki(args.days)
    course = collect_course(args.days)
    reading = collect_reading(args.days)
    focus = round(anki["today"]["minutes"] + reading["today"]["minutes"])
    payload = {
        "updatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": {"date": datetime.now().date().isoformat(), "focusMinutes": focus},
        "anki": anki,
        "course": course,
        "reading": reading,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {OUTPUT}")


if __name__ == "__main__":
    main()
