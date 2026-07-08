#!/usr/bin/env python3
"""Add Chinese context meanings to selected Anki decks from an existing bilingual deck.

This script intentionally uses Anki as the source of truth:
  - Source Chinese meanings come from an existing deck in the same collection.
  - Target notes are enriched in their existing Note field.
  - No separate vocabulary database is maintained.

Safety:
  - Dry-run by default.
  - Refuses to write while Anki is running.
  - Creates a timestamped backup before applying changes.
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_COLLECTION = Path.home() / "AppData" / "Roaming" / "Anki2" / "账户 1" / "collection.anki2"
SOURCE_DECK = "French 2-Month Intensive 2500"
TARGET_DECKS = [
    "5000 Most Common French Words Pt. 2\x1f[1] Main Course\x1f[b] Option 1: Canadian French Audio\x1fI) French to English",
    "5000 Most Common French Words\x1f[1] Main Course\x1f[a] Option 1: Parisian French Audio\x1fI) French to English (Start here)",
]
MARKER = "中文语境义："


def clean(value: str | None) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", text).strip()


def display_deck(name: str) -> str:
    return name.replace("\x1f", "::")


def is_anki_running() -> bool:
    if sys.platform != "win32":
        return False
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Get-Process anki -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return bool(result.stdout.strip())


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.create_collation("unicase", lambda a, b: (a.casefold() > b.casefold()) - (a.casefold() < b.casefold()))
    return con


def field_names(cur: sqlite3.Cursor, ntid: int) -> list[str]:
    return [row[0] for row in cur.execute("select name from fields where ntid=? order by ord", (ntid,))]


def row_dict(fields: list[str], flds: str) -> dict[str, str]:
    values = flds.split("\x1f")
    return {name: values[index] if index < len(values) else "" for index, name in enumerate(fields)}


def pack_fields(fields: list[str], values: dict[str, str]) -> str:
    return "\x1f".join(values.get(name, "") for name in fields)


def deck_id(cur: sqlite3.Cursor, name: str) -> int | None:
    row = cur.execute("select id from decks where name=?", (name,)).fetchone()
    return int(row[0]) if row else None


@dataclass
class SourceMeaning:
    chinese: str
    english: str
    sentence: str


def build_source_map(cur: sqlite3.Cursor, source_name: str) -> dict[str, SourceMeaning]:
    did = deck_id(cur, source_name)
    if did is None:
        raise SystemExit(f"Source deck not found: {display_deck(source_name)}")
    source: dict[str, SourceMeaning] = {}
    rows = cur.execute(
        "select distinct n.mid,n.flds from cards c join notes n on n.id=c.nid where c.did=?",
        (did,),
    ).fetchall()
    for mid, flds in rows:
        fields = field_names(cur, int(mid))
        note = row_dict(fields, flds)
        french = clean(note.get("French")).casefold()
        chinese = clean(note.get("Chinese"))
        if french and chinese:
            source[french] = SourceMeaning(chinese, clean(note.get("English")), clean(note.get("Sentence")))
    return source


def target_notes(cur: sqlite3.Cursor, target_names: list[str]) -> list[tuple[int, int, str, str]]:
    result: list[tuple[int, int, str, str]] = []
    for name in target_names:
        did = deck_id(cur, name)
        if did is None:
            print(f"Warning: target deck not found: {display_deck(name)}")
            continue
        rows = cur.execute(
            "select distinct n.id,n.mid,n.flds,d.name from cards c join notes n on n.id=c.nid join decks d on d.id=c.did where c.did=?",
            (did,),
        ).fetchall()
        result.extend((int(nid), int(mid), flds, deck_name) for nid, mid, flds, deck_name in rows)
    return result


def make_note_text(meaning: SourceMeaning, target: dict[str, str]) -> str:
    english = clean(target.get("Basic meanings of word"))
    example = clean(target.get("Example sentences without translation")) or clean(target.get("Example sentences"))
    pieces = [f"{MARKER}{meaning.chinese}"]
    if english:
        pieces.append(f"英文释义：{english}")
    if example:
        pieces.append(f"法语语境：{example}")
    return "<br>".join(pieces)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["deck", "note_id", "word", "chinese", "english", "example", "status"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich active French Anki decks with Chinese context meanings.")
    parser.add_argument("--collection", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--source-deck", default=SOURCE_DECK)
    parser.add_argument("--target-deck", action="append", dest="target_decks")
    parser.add_argument("--preview", type=Path, default=Path("data/anki_chinese_preview.csv"))
    parser.add_argument("--unmatched", type=Path, default=Path("data/anki_chinese_unmatched.csv"))
    parser.add_argument("--apply", action="store_true", help="Actually update the Anki collection. Close Anki first.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing Note content that already contains 中文语境义.")
    args = parser.parse_args()

    if not args.collection.exists():
        raise SystemExit(f"Collection not found: {args.collection}")
    if args.apply and is_anki_running():
        raise SystemExit("Anki is running. Close Anki before using --apply.")

    con = connect(args.collection)
    cur = con.cursor()
    source = build_source_map(cur, args.source_deck)
    targets = target_notes(cur, args.target_decks or TARGET_DECKS)

    preview_rows: list[dict[str, str]] = []
    unmatched_rows: list[dict[str, str]] = []
    updates: list[tuple[str, int]] = []
    now = int(time.time())

    for nid, mid, flds, deck_name in targets:
        fields = field_names(cur, mid)
        note = row_dict(fields, flds)
        word = clean(note.get("Word")).casefold()
        note_text = note.get("Note", "")
        if not word:
            continue
        meaning = source.get(word)
        if not meaning:
            unmatched_rows.append({
                "deck": display_deck(deck_name),
                "note_id": str(nid),
                "word": clean(note.get("Word")),
                "chinese": "",
                "english": clean(note.get("Basic meanings of word")),
                "example": clean(note.get("Example sentences without translation")) or clean(note.get("Example sentences")),
                "status": "no-local-chinese-source",
            })
            continue
        if MARKER in note_text and not args.overwrite:
            status = "already-enriched"
        else:
            addition = make_note_text(meaning, note)
            note["Note"] = addition if not clean(note_text) or args.overwrite else note_text + "<br><br>" + addition
            updates.append((pack_fields(fields, note), nid))
            status = "will-update" if not args.apply else "updated"
        preview_rows.append({
            "deck": display_deck(deck_name),
            "note_id": str(nid),
            "word": clean(note.get("Word")),
            "chinese": meaning.chinese,
            "english": clean(note.get("Basic meanings of word")),
            "example": clean(note.get("Example sentences without translation")) or clean(note.get("Example sentences")),
            "status": status,
        })

    write_csv(args.preview, preview_rows)
    write_csv(args.unmatched, unmatched_rows)

    if args.apply and updates:
        backup = args.collection.with_name(args.collection.name + f".backup-before-chinese-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(args.collection, backup)
        cur.executemany("update notes set flds=?, mod=?, usn=-1 where id=?", [(flds, now, nid) for flds, nid in updates])
        cur.execute("update col set mod=?, usn=-1", (now * 1000,))
        con.commit()
        print(f"Applied {len(updates)} updates. Backup: {backup}")
    else:
        con.rollback()
        print(f"Dry run only. Matched {len(preview_rows)} notes, {len(unmatched_rows)} unmatched.")
        print(f"Preview: {args.preview}")
        print(f"Unmatched: {args.unmatched}")

    con.close()


if __name__ == "__main__":
    main()
