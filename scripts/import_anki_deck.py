#!/usr/bin/env python3
"""Import a French Anki deck export into the morphology trainer cache.

Supported inputs:
  - CSV / TSV exported from Anki
  - APKG deck packages

The generated JSON is a derived static cache for the website. Anki remains the
source of truth; re-run this script after editing the deck.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "French",
    "Chinese",
    "Gender",
    "PartOfSpeech",
    "Lemma",
    "Plural",
    "Theme",
    "Level",
    "FixedPhrases",
    "ConjugationGroup",
    "PastParticiple",
    "Notes",
]

ALIASES = {
    "french": "French",
    "fr": "French",
    "word": "French",
    "mot": "French",
    "chinese": "Chinese",
    "zh": "Chinese",
    "cn": "Chinese",
    "meaning": "Chinese",
    "gender": "Gender",
    "genre": "Gender",
    "partofspeech": "PartOfSpeech",
    "pos": "PartOfSpeech",
    "lemma": "Lemma",
    "base": "Lemma",
    "plural": "Plural",
    "theme": "Theme",
    "topic": "Theme",
    "level": "Level",
    "fixedphrases": "FixedPhrases",
    "phrases": "FixedPhrases",
    "conjugationgroup": "ConjugationGroup",
    "group": "ConjugationGroup",
    "pastparticiple": "PastParticiple",
    "participepasse": "PastParticiple",
    "notes": "Notes",
}

OPTIONAL_FORM_ALIASES = {
    "presentje": ("conjugations", "present", "je"),
    "presenttu": ("conjugations", "present", "tu"),
    "presentil": ("conjugations", "present", "il"),
    "presentelle": ("conjugations", "present", "elle"),
    "presentnous": ("conjugations", "present", "nous"),
    "presentvous": ("conjugations", "present", "vous"),
    "presentils": ("conjugations", "present", "ils"),
    "presentelles": ("conjugations", "present", "elles"),
    "conjugations": ("conjugations_json",),
    "examples": ("examples",),
    "example": ("examples",),
}


def clean(value: Any) -> str:
    text = "" if value is None else str(value)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text).strip()


def key_for(name: str) -> str | None:
    compact = re.sub(r"[^a-z0-9]", "", name.lower())
    return ALIASES.get(compact)


def split_list(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[;\n|]+", value)
    return [clean(part) for part in parts if clean(part)]


def detect_dialect(path: Path) -> csv.Dialect:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;")
    except csv.Error:
        dialect = csv.excel_tab if "\t" in sample else csv.excel
        return dialect


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    dialect = detect_dialect(path)
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, dialect=dialect)
        rows = [{clean(k): clean(v) for k, v in row.items()} for row in reader]
        return rows, [clean(x) for x in (reader.fieldnames or [])]


@dataclass
class ApkgRows:
    rows: list[dict[str, str]]
    field_names: list[str]


def read_apkg(path: Path) -> ApkgRows:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(path) as archive:
            db_name = "collection.anki21b" if "collection.anki21b" in archive.namelist() else "collection.anki2"
            archive.extract(db_name, tmp_path)
        con = sqlite3.connect(tmp_path / db_name)
        try:
            models = json.loads(con.execute("select models from col").fetchone()[0])
            model_fields: dict[int, list[str]] = {}
            for mid, model in models.items():
                fields = sorted(model.get("flds", []), key=lambda x: x.get("ord", 0))
                model_fields[int(mid)] = [field.get("name", "") for field in fields]
            rows: list[dict[str, str]] = []
            all_fields: list[str] = []
            for mid, flds in con.execute("select mid, flds from notes"):
                names = model_fields.get(int(mid), [])
                values = str(flds).split("\x1f")
                row = {names[i] if i < len(names) else f"Field{i + 1}": clean(value) for i, value in enumerate(values)}
                rows.append(row)
                for name in names:
                    if name and name not in all_fields:
                        all_fields.append(name)
            return ApkgRows(rows, all_fields)
        finally:
            con.close()


def put_nested(target: dict[str, Any], path: tuple[str, ...], value: str) -> None:
    node = target
    for part in path[:-1]:
        node = node.setdefault(part, {})
    node[path[-1]] = value


def normalize_row(row: dict[str, str], index: int) -> dict[str, Any]:
    normalized = {field: "" for field in REQUIRED_FIELDS}
    extra: dict[str, Any] = {}
    for source_key, raw_value in row.items():
        value = clean(raw_value)
        if not value:
            continue
        canonical = key_for(source_key)
        if canonical:
            normalized[canonical] = value
            continue
        compact = re.sub(r"[^a-z0-9]", "", source_key.lower())
        optional = OPTIONAL_FORM_ALIASES.get(compact)
        if optional:
            if optional == ("conjugations_json",):
                try:
                    extra["conjugations"] = json.loads(value)
                except json.JSONDecodeError:
                    extra["conjugationsText"] = value
            elif optional == ("examples",):
                extra["examples"] = split_list(value)
            else:
                put_nested(extra, optional, value)
    fixed_phrases = split_list(normalized["FixedPhrases"])
    examples = extra.get("examples", [])
    entry = {
        "id": f"anki-{index + 1}",
        "french": normalized["French"],
        "chinese": normalized["Chinese"],
        "gender": normalized["Gender"],
        "partOfSpeech": normalized["PartOfSpeech"],
        "lemma": normalized["Lemma"],
        "plural": normalized["Plural"],
        "theme": normalized["Theme"],
        "level": normalized["Level"],
        "fixedPhrases": fixed_phrases,
        "conjugationGroup": normalized["ConjugationGroup"],
        "pastParticiple": normalized["PastParticiple"],
        "notes": normalized["Notes"],
        "examples": examples,
    }
    if "conjugations" in extra:
        entry["conjugations"] = extra["conjugations"]
    if "conjugationsText" in extra:
        entry["conjugationsText"] = extra["conjugationsText"]
    return entry


def import_deck(source: Path) -> tuple[list[dict[str, Any]], list[str]]:
    suffix = source.suffix.lower()
    if suffix == ".apkg":
        result = read_apkg(source)
        rows, fields = result.rows, result.field_names
    elif suffix in {".csv", ".tsv", ".txt"}:
        rows, fields = read_csv(source)
    else:
        raise SystemExit(f"Unsupported input type: {source.suffix}. Use .apkg, .csv, .tsv, or .txt.")
    entries = [normalize_row(row, index) for index, row in enumerate(rows)]
    entries = [entry for entry in entries if entry["french"] or entry["lemma"] or entry["fixedPhrases"]]
    return entries, fields


def main() -> None:
    parser = argparse.ArgumentParser(description="Import an Anki export for the TCF morphology trainer.")
    parser.add_argument("source", type=Path, help="Path to .apkg, .csv, .tsv, or .txt exported from Anki.")
    parser.add_argument("--out", type=Path, default=Path("data/morphology.json"), help="Output JSON path.")
    args = parser.parse_args()
    entries, source_fields = import_deck(args.source)
    missing = [field for field in REQUIRED_FIELDS if not any(key_for(name) == field for name in source_fields)]
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": {"type": args.source.suffix.lower().lstrip("."), "path": str(args.source)},
        "requiredFields": REQUIRED_FIELDS,
        "sourceFields": source_fields,
        "missingRequiredFields": missing,
        "entries": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Imported {len(entries)} entries -> {args.out}")
    if missing:
        print("Missing recommended fields: " + ", ".join(missing))


if __name__ == "__main__":
    main()
