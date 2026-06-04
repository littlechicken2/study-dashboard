import argparse
import json
from datetime import date
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "data" / "reading_log.json"


def main():
    parser = argparse.ArgumentParser(description="Add one reading training session.")
    parser.add_argument("--questions", type=int, required=True)
    parser.add_argument("--correct", type=int, required=True)
    parser.add_argument("--minutes", type=int, required=True)
    parser.add_argument("--sets", type=int, default=1)
    parser.add_argument("--source", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    data = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else {"entries": []}
    data["entries"].append(vars(args))
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Added reading session for {args.date}")


if __name__ == "__main__":
    main()
