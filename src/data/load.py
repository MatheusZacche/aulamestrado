"""Carregamento e persistência do banco de questões."""
from __future__ import annotations

import json
from pathlib import Path

from .schema import Question, QuestionBank, empty_bank

ROOT = Path(__file__).resolve().parents[2]
BANK_PATH = ROOT / "data" / "questions.json"
TOPICS_PATH = ROOT / "data" / "topics.json"


def load_bank(path: Path | None = None) -> QuestionBank:
    p = path or BANK_PATH
    if not p.exists():
        return empty_bank()
    raw = json.loads(p.read_text(encoding="utf-8"))
    return QuestionBank.model_validate(raw)


def save_bank(bank: QuestionBank, path: Path | None = None) -> None:
    p = path or BANK_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        bank.model_dump_json(indent=2, exclude_none=False),
        encoding="utf-8",
    )


def add_or_update(bank: QuestionBank, q: Question) -> QuestionBank:
    existing_ids = {x.id: i for i, x in enumerate(bank.questions)}
    if q.id in existing_ids:
        bank.questions[existing_ids[q.id]] = q
    else:
        bank.questions.append(q)
    return bank


def load_topics() -> dict:
    return json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
