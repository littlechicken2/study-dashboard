import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "data" / "reading_progress.json"
SESSION = ROOT / "data" / "reading_session.json"


def main():
    try:
        data = json.loads(PROGRESS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {"entries": []}
    baselines = {}
    for entry in data.get("entries", []):
        test = str(entry.get("test", ""))
        if not test:
            continue
        previous = baselines.get(test)
        if previous is None or str(entry.get("capturedAt", "")) >= previous["capturedAt"]:
            baselines[test] = {
                "answered": int(entry.get("answered", 0) or 0),
                "correct": int(entry.get("correct", 0) or 0),
                "seconds": int(entry.get("seconds", 0) or 0),
                "capturedAt": str(entry.get("capturedAt", "")),
            }
    payload = {
        "startedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "baselines": baselines,
    }
    SESSION.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reading session reset with {len(baselines)} test baseline(s).")


if __name__ == "__main__":
    main()
