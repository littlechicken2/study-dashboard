#!/usr/bin/env python3
"""Rebuild concise Chinese meanings for the combined Anki deck."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_anki_from_frdic as frdic  # noqa: E402


SOURCE_DECK = "French 2-Month Intensive 2500"
CONTEXT_BEGIN = "<!-- context-cn:begin -->"
CONTEXT_END = "<!-- context-cn:end -->"
CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "anki_context_translations.json"

# These are the cards currently in learning/due state. The English gloss on the
# card determines the intended sense; French dictionary entries are secondary.
CURATED_CONTEXT = {
    "aîné": "年长的；最年长的；长子或长女；前辈",
    "tôt": "早；早些时候",
    "gentil": "友善的；善良的；亲切的",
    "soirée": "晚上；晚会",
    "patron": "老板；雇主",
    "tirer": "拉；拖；拔出",
    "montre": "手表",
    "douleur": "疼痛；痛苦",
    "discours": "演讲；讲话；论述",
    "réveiller": "叫醒；唤醒",
    "rock": "摇滚乐",
    "lourd": "重的；沉重的",
    "bouffe": "食物；吃的东西（口语）",
    "désir": "愿望；欲望",
    "remplir": "装满；填写",
    "printemps": "春天；春季",
    "reconnaître": "认出；承认；认可",
    "participer": "参加；参与",
    "causer": "引起；造成",
    "héritage": "遗产；传承",
    "débrouiller": "解开；理清",
    "entrain": "活力；兴致；欢快",
    "accomplir": "完成；实现",
    "facture": "发票；账单",
    "équilibre": "平衡；均衡",
    "cesser": "停止；终止",
    "veiller": "照看；留意；守护",
    "répétition": "重复；排练",
    "accorder": "给予；授予",
    "document": "文件；文档；资料",
    "archer": "弓箭手",
    "louche": "可疑的；不正当的",
    "insensé": "疯狂的；愚蠢的；荒谬的",
    "structure": "结构；构造",
    "vif": "活泼的；鲜明的；明亮的",
    "impressionner": "给人留下深刻印象；使震撼",
    "pénible": "辛苦的；困难的；令人痛苦的",
    "surprendre": "使惊讶；使措手不及",
    "cicatrice": "疤痕；伤疤",
    "sonner": "响；鸣；按铃",
    "démarrer": "启动；开始",
    "adopter": "采用；收养",
    "mallette": "公文包；小手提箱",
    "mouillé": "湿的；潮湿的",
    "gentillesse": "友善；善意；体贴",
    "horaire": "时刻表；时间安排",
    "carrière": "职业；事业；职业生涯",
    "château": "城堡；庄园",
    "colis": "包裹；邮包",
    "championnat": "锦标赛；冠军赛",
    "conviction": "信念；确信",
    "manche": "袖子；回合；一局比赛",
    "orbite": "轨道；眼窝",
    "pédale": "踏板；脚蹬",
    "plonger": "潜水；跳入；使陷入",
    "toast": "烤面包片；祝酒词",
    "trottoir": "人行道",
    "timide": "害羞的；胆怯的",
    "ambiance": "气氛；氛围",
    "ère": "时代；纪元",
    "cheville": "脚踝；踝关节",
    "drame": "戏剧；悲剧性事件",
    "maïs": "玉米；玉蜀黍",
    "mensonge": "谎言；谎话；假话",
}


def plain(value: str | None) -> str:
    return frdic.clean(re.sub(r"<[^>]+>", " ", value or ""))


def strip_context_block(note: str) -> str:
    value = re.sub(
        re.escape(CONTEXT_BEGIN) + r".*?" + re.escape(CONTEXT_END),
        "",
        note or "",
        flags=re.DOTALL,
    ).strip()
    value = re.sub(r"^(?:\s*<br>\s*)+", "", value)
    return re.sub(r"(?:\s*<br>\s*)+$", "", value).strip()


def source_map() -> dict[str, str]:
    note_ids = frdic.anki("findNotes", {"query": f'deck:"{SOURCE_DECK}"'})
    result: dict[str, str] = {}
    for note in frdic.load_notes(note_ids):
        fields = frdic.note_fields(note)
        word = plain(fields.get("French")).casefold()
        chinese = plain(fields.get("Chinese"))
        if word and chinese:
            result[word] = chinese
    return result


def load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {str(key).casefold(): str(value) for key, value in data.items() if value}


def make_context_note(
    chinese: str,
    previous_note: str,
) -> str:
    body = f'<div class="context-meaning"><b>中文：</b>{html.escape(chinese)}</div>'
    block = f"{CONTEXT_BEGIN}{body}{CONTEXT_END}"
    preserved = strip_context_block(frdic.strip_old_enrichment(previous_note))
    return block if not preserved else f"{block}<br><br>{preserved}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore context-aware Chinese meanings in Anki.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    old_chinese = source_map()
    target_notes = frdic.load_notes(frdic.find_target_notes(frdic.TARGET_DECK))
    cache = load_cache()
    updates: list[tuple[int, str]] = []
    counts = {"curated": 0, "original": 0, "offline": 0, "missing": 0}

    for note in target_notes:
        if note.get("modelName") not in frdic.TARGET_MODELS:
            continue
        fields = frdic.note_fields(note)
        word = plain(fields.get("Word"))
        key = word.casefold()
        current_note = fields.get("Note", "")

        if key in CURATED_CONTEXT:
            chinese, source = CURATED_CONTEXT[key], "curated"
        elif key in old_chinese:
            chinese, source = old_chinese[key], "original"
        elif key in cache:
            chinese, source = cache[key], "offline"
        else:
            chinese, source = "", "missing"
        counts[source] += 1
        if not chinese:
            continue
        rebuilt = make_context_note(chinese, current_note)
        if rebuilt != current_note:
            updates.append((int(note["noteId"]), rebuilt))

    print(
        f"Curated: {counts['curated']}; restored: {counts['original']}; "
        f"offline: {counts['offline']}; missing: {counts['missing']}"
    )
    print(f"Updates: {len(updates)}; apply={args.apply}")
    if args.apply:
        frdic.apply_updates(updates)


if __name__ == "__main__":
    main()
