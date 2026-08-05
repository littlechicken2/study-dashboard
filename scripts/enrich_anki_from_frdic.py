#!/usr/bin/env python3
"""Replace weak/missing Chinese Anki meanings with French Assistant entries."""
from __future__ import annotations

import argparse
import html
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


ANKI_URL = "http://127.0.0.1:8766"
TARGET_DECK = "French Daily Audio + Reading"
TARGET_MODELS = {
    "5000 French Words 2.0 (F to E)",
    "5000 French Words 2.0 (F to E) C",
}
STATUS_PATH = Path(__file__).resolve().parents[1] / "data" / "anki_frdic_enrichment_status.json"
FRDIC_BEGIN = "<!-- frdic-cn:begin -->"
FRDIC_END = "<!-- frdic-cn:end -->"
LEGACY_MARKER = "中文语境义："
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")
CURATED_FALLBACKS = {
    "veine": "静脉；血管；矿脉；（口语）运气",
    "saoul": "醉的；喝醉的",
    "allure": "外貌，样子；速度，步调",
    "hache": "斧头",
    "angoisse": "焦虑，恐惧；痛苦",
    "lessive": "洗衣；洗涤剂",
    "applaudissements": "掌声，喝彩",
    "canne": "手杖；棍；甘蔗",
    "coude": "肘，肘部",
    "ruse": "诡计，计谋；狡猾",
    "patte": "（动物的）爪，脚",
    "paysage": "风景，景色",
    "fosse": "坑；沟；墓穴",
    "concurrence": "竞争；竞争者",
    "carbone": "碳",
    "boucle": "环，圈；卷发；耳环",
    "sinistre": "阴森的，凶险的；不祥的",
    "comble": "顶点，极点；屋顶空间",
    "cuivre": "铜；铜器",
    "amiral": "海军上将",
    "canon": "大炮，火炮",
    "muscle": "肌肉",
    "peigne": "梳子",
    "colle": "胶水，黏合剂",
    "couple": "一对；情侣，夫妻",
    "peuple": "人民；民族",
    "vente": "销售，出售",
    "tranche": "片，切片；部分",
    "onde": "波，波浪",
    "intrigue": "阴谋；（故事的）情节",
    "perle": "珍珠",
    "parachute": "降落伞",
    "suture": "缝合；缝合线",
    "module": "模块，单元",
    "laine": "羊毛；毛线",
    "chiffre": "数字；数额",
    "indigne": "不配的；卑劣的",
    "grade": "等级；军衔",
    "peluche": "绒毛；毛绒织物；毛绒玩具",
    "bronze": "青铜；青铜器",
    "poivre": "胡椒；胡椒粉",
    "vanille": "香草；香草味",
    "filtre": "过滤器；滤网",
    "email": "电子邮件",
    "fraise": "草莓",
    "marbre": "大理石",
    "pente": "斜坡；坡度",
    "mature": "成熟的",
    "sonde": "探测器；探针",
    "architecture": "建筑；建筑学；结构",
    "offense": "冒犯；侮辱",
    "pellicule": "胶片；薄膜",
    "combine": "诡计；计策",
    "baleine": "鲸",
    "lame": "刀刃；薄片",
    "outrage": "侮辱；严重冒犯",
    "pyramide": "金字塔",
    "ongle": "指甲；爪",
    "planque": "（口语）藏身处",
    "voile": "面纱；薄纱",
    "corne": "角；角质",
    "poire": "梨",
    "rame": "列车车组；桨",
    "valve": "阀门；瓣膜",
    "courbe": "曲线；弯曲",
    "mire": "准星；瞄准目标",
    "carrosse": "马车",
    "immature": "不成熟的；未熟的",
    "paume": "手掌",
    "ouvrage": "作品；工程；工作",
    "valide": "有效的；健全的",
    "rive": "河岸，岸边",
    "lisse": "光滑的；平整的",
    "meuble": "家具",
    "artefact": "人工制品；假象",
    "consigne": "指示，命令；寄存",
    "naufrage": "沉船；海难",
    "entrave": "阻碍；束缚",
    "cire": "蜡",
    "illustre": "著名的，杰出的",
    "fissure": "裂缝，裂纹",
    "forge": "锻造厂；铁匠铺",
    "colon": "殖民者；移民定居者",
    "ride": "皱纹；波纹",
    "broche": "胸针；烤肉叉",
    "ardoise": "石板；板岩",
    "loupe": "放大镜",
    "moule": "模具，铸模",
    "ruche": "蜂箱；蜂巢",
    "affiche": "海报；布告；招贴",
}


def anki(action: str, params: dict[str, Any] | None = None) -> Any:
    payload = json.dumps({"action": action, "version": 6, "params": params or {}}).encode("utf-8")
    request = Request(ANKI_URL, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result.get("result")


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def unique(values: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = clean(value)
        key = normalized.casefold()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


@dataclass(frozen=True)
class DictionaryEntry:
    word: str
    part_of_speech: str
    meanings: list[str]
    url: str


def fetch_entry(word: str, delay: float, retries: int = 3) -> DictionaryEntry:
    url = f"https://cn0.eudic.net/dicts/fr/{quote(word, safe='')}"
    legacy_url = f"https://legacy.frdic.com/SearchDic.aspx?word={quote(word, safe='')}"
    last_error: Exception | None = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8",
    }
    legacy_meanings: list[str] = []
    for attempt in range(retries):
        try:
            request = Request(legacy_url, headers=headers)
            with urlopen(request, timeout=10) as response:
                source = response.read().decode("utf-8", errors="replace")
            soup = BeautifulSoup(source, "html.parser")
            concise = soup.select_one("#DicFCChild")
            concise_lines = re.split(r"[\r\n]+", concise.get_text("\n", strip=True) if concise else "")
            meanings = unique([line for line in concise_lines if CHINESE_RE.search(line)], 6)
            if meanings:
                legacy_meanings = meanings
                if not any("..." in value or "…" in value for value in meanings):
                    time.sleep(delay)
                    return DictionaryEntry(word=word, part_of_speech="", meanings=meanings, url=url)
                break
            raise ValueError("no Chinese definition found")
        except Exception as error:  # Network and changing dictionary markup are both retryable.
            last_error = error
            time.sleep(max(delay, 0.5) * (attempt + 1))

    # The modern page is slower and sometimes renders Chinese as images, so use it
    # only once to complete a truncated legacy entry.
    try:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=10) as response:
            source = response.read().decode("utf-8", errors="replace")
        soup = BeautifulSoup(source, "html.parser")
        section = soup.select_one("#ExpFCchild")
        if section:
            parts = unique([node.get_text(" ", strip=True) for node in section.select(".cara")], 3)
            definition_nodes = section.select(".exp")
            modern_meanings = unique(
                [
                    node.get_text(" ", strip=True)
                    for node in definition_nodes
                    if not node.select_one("img.dictimgtoword") and CHINESE_RE.search(node.get_text())
                ],
                6,
            )
            if modern_meanings:
                return DictionaryEntry(
                    word=word,
                    part_of_speech=" / ".join(parts),
                    meanings=modern_meanings,
                    url=url,
                )
    except Exception as error:
        last_error = error

    if legacy_meanings:
        return DictionaryEntry(word=word, part_of_speech="", meanings=legacy_meanings, url=url)
    curated = CURATED_FALLBACKS.get(word.casefold())
    if curated:
        return DictionaryEntry(word=word, part_of_speech="", meanings=[curated], url=url)
    raise RuntimeError(f"{word}: {last_error}")


def note_fields(note: dict[str, Any]) -> dict[str, str]:
    return {name: str(field.get("value", "")) for name, field in note.get("fields", {}).items()}


def strip_old_enrichment(note: str) -> str:
    value = re.sub(
        re.escape(FRDIC_BEGIN) + r".*?" + re.escape(FRDIC_END),
        "",
        note or "",
        flags=re.DOTALL,
    )
    legacy_at = value.find(LEGACY_MARKER)
    if legacy_at >= 0:
        value = value[:legacy_at]
    return re.sub(r"(?:\s*<br>\s*)+$", "", value).strip()


def make_note(entry: DictionaryEntry, previous_note: str) -> str:
    pos = f"<span style=\"color:#777\">{html.escape(entry.part_of_speech)}</span><br>" if entry.part_of_speech else ""
    meanings = "<br>".join(html.escape(value) for value in entry.meanings)
    block = (
        f"{FRDIC_BEGIN}"
        f"<div class=\"frdic-chinese\"><b>法汉：</b><br>{pos}{meanings}"
        f"<br><a href=\"{html.escape(entry.url, quote=True)}\">法语助手词典</a></div>"
        f"{FRDIC_END}"
    )
    preserved = strip_old_enrichment(previous_note)
    return block if not preserved else f"{block}<br><br>{preserved}"


def find_target_notes(deck: str) -> list[int]:
    queries = [
        f'deck:"{deck}" is:learn',
        f'deck:"{deck}" is:due',
        f'deck:"{deck}" is:new',
        f'deck:"{deck}"',
    ]
    ordered: list[int] = []
    seen: set[int] = set()
    for query in queries:
        for note_id in anki("findNotes", {"query": query}):
            if note_id not in seen:
                seen.add(note_id)
                ordered.append(note_id)
    return ordered


def load_notes(note_ids: list[int]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for start in range(0, len(note_ids), 500):
        result.extend(anki("notesInfo", {"notes": note_ids[start : start + 500]}))
    return result


def apply_updates(updates: list[tuple[int, str]]) -> None:
    for start in range(0, len(updates), 50):
        actions = [
            {
                "action": "updateNoteFields",
                "params": {"note": {"id": note_id, "fields": {"Note": note_text}}},
            }
            for note_id, note_text in updates[start : start + 50]
        ]
        results = anki("multi", {"actions": actions})
        errors = [
            item.get("error")
            for item in results
            if isinstance(item, dict) and item.get("error")
        ]
        if errors:
            raise RuntimeError("; ".join(errors))


def write_status(payload: dict[str, Any]) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill Anki Chinese meanings from French Assistant.")
    parser.add_argument("--deck", default=TARGET_DECK)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true", help="Re-fetch entries already marked as French Assistant data.")
    parser.add_argument("--apply", action="store_true", help="Write definitions to Anki instead of previewing them.")
    args = parser.parse_args()

    anki("version")
    all_notes = load_notes(find_target_notes(args.deck))
    candidates: list[tuple[int, str, str]] = []
    for note in all_notes:
        if note.get("modelName") not in TARGET_MODELS:
            continue
        fields = note_fields(note)
        word = clean(re.sub(r"<[^>]+>", " ", fields.get("Word", "")))
        current_note = fields.get("Note", "")
        if not word or (FRDIC_BEGIN in current_note and not args.overwrite):
            continue
        candidates.append((int(note["noteId"]), word, current_note))
    if args.limit > 0:
        candidates = candidates[: args.limit]

    started = time.time()
    completed = 0
    failed: list[dict[str, str]] = []
    pending_updates: list[tuple[int, str]] = []
    preview: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal pending_updates
        if args.apply and pending_updates:
            apply_updates(pending_updates)
        pending_updates = []
        write_status(
            {
                "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "deck": args.deck,
                "candidatesThisRun": len(candidates),
                "completedThisRun": completed,
                "failedThisRun": len(failed),
                "applied": args.apply,
                "elapsedSeconds": round(time.time() - started, 1),
                "failed": failed[-100:],
                "preview": preview[:20],
            }
        )

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(fetch_entry, word, max(0, args.delay)): (note_id, word, old_note)
            for note_id, word, old_note in candidates
        }
        for future in as_completed(future_map):
            note_id, word, old_note = future_map[future]
            try:
                entry = future.result()
                note_text = make_note(entry, old_note)
                pending_updates.append((note_id, note_text))
                completed += 1
                if len(preview) < 20:
                    preview.append({"word": word, "partOfSpeech": entry.part_of_speech, "meanings": entry.meanings})
            except Exception as error:
                failed.append({"word": word, "error": str(error)})
            if len(pending_updates) >= max(1, args.batch_size):
                flush()
                print(f"Completed {completed}/{len(candidates)}; failed {len(failed)}", flush=True)
    flush()
    print(
        f"Finished: {completed}/{len(candidates)} definitions; {len(failed)} failed; "
        f"elapsed {time.time() - started:.1f}s; applied={args.apply}",
        flush=True,
    )


if __name__ == "__main__":
    main()
