"""Persistência local de progresso do usuário.

Arquivo: data/user_progress.json (gitignored).
Modelo: {
  "answers": {question_id: {"chosen": "a", "correct": true, "ts": "...", "confianca": "chute|certeza"}},
  "bookmarked": [question_id, ...],
  "notes": {question_id: "texto"},
  "sessions": [{"started": "...", "ended": "...", "score": 12, "total": 20, "modo": "simulado"}]
}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROGRESS_PATH = ROOT / "data" / "user_progress.json"


def _empty() -> dict[str, Any]:
    return {"answers": {}, "bookmarked": [], "notes": {}, "sessions": []}


def load_progress() -> dict[str, Any]:
    if not PROGRESS_PATH.exists():
        return _empty()
    try:
        return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty()


def save_progress(data: dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_answer(qid: str, chosen: str, correct: bool, confianca: str = "") -> None:
    p = load_progress()
    p["answers"][qid] = {
        "chosen": chosen,
        "correct": correct,
        "ts": datetime.now(timezone.utc).isoformat(),
        "confianca": confianca,
    }
    save_progress(p)


def toggle_bookmark(qid: str) -> bool:
    p = load_progress()
    if qid in p["bookmarked"]:
        p["bookmarked"].remove(qid)
        save_progress(p)
        return False
    p["bookmarked"].append(qid)
    save_progress(p)
    return True


def save_note(qid: str, text: str) -> None:
    p = load_progress()
    if text.strip():
        p["notes"][qid] = text
    else:
        p["notes"].pop(qid, None)
    save_progress(p)


def record_session(score: int, total: int, modo: str, duration_s: float) -> None:
    p = load_progress()
    p["sessions"].append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "total": total,
            "modo": modo,
            "duration_s": duration_s,
        }
    )
    save_progress(p)
