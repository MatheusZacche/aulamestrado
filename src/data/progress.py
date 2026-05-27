"""Persistência de progresso do usuário (single-user).

Dois backends:
  - JSONBackend: arquivo local data/user_progress.json. Bom pra dev/local.
  - SupabaseBackend: tabelas no Postgres do Supabase, sem autenticação
    (app single-user; proteção via anon key em Streamlit Secrets).

Seleção automática:
  - Se SUPABASE_URL e SUPABASE_ANON_KEY estão configurados → Supabase.
  - Senão → JSON local.

API pública (igual antes):
  load_progress() -> dict {answers, bookmarked, notes, sessions}
  record_answer(qid, chosen, correct, confianca)
  toggle_bookmark(qid) -> bool
  save_note(qid, text)
  record_session(score, total, modo, duration_s)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
PROGRESS_PATH = ROOT / "data" / "user_progress.json"


# ============================================================
# Interface
# ============================================================


class ProgressBackend(Protocol):
    name: str
    def load(self) -> dict[str, Any]: ...
    def record_answer(self, qid: str, chosen: str, correct: bool, confianca: str) -> None: ...
    def record_simulado_answers(self, answers: dict[str, dict[str, Any]]) -> None: ...
    def toggle_bookmark(self, qid: str) -> bool: ...
    def save_note(self, qid: str, text: str) -> None: ...
    def record_session(self, score: int, total: int, modo: str, duration_s: float) -> None: ...


# ============================================================
# Backend 1: JSON local (fallback)
# ============================================================


def _empty_state() -> dict[str, Any]:
    return {"answers": {}, "simulado_answers": {}, "bookmarked": [], "notes": {}, "sessions": []}


class JSONBackend:
    name = "json_local"

    def load(self) -> dict[str, Any]:
        if not PROGRESS_PATH.exists():
            return _empty_state()
        try:
            data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
            if "simulado_answers" not in data:
                data["simulado_answers"] = {}
            return data
        except json.JSONDecodeError:
            return _empty_state()

    def _save(self, data: dict[str, Any]) -> None:
        PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def record_answer(self, qid: str, chosen: str, correct: bool, confianca: str = "") -> None:
        p = self.load()
        p["answers"][qid] = {
            "chosen": chosen,
            "correct": correct,
            "ts": datetime.now(timezone.utc).isoformat(),
            "confianca": confianca,
        }
        self._save(p)

    def toggle_bookmark(self, qid: str) -> bool:
        p = self.load()
        if qid in p["bookmarked"]:
            p["bookmarked"].remove(qid)
            self._save(p)
            return False
        p["bookmarked"].append(qid)
        self._save(p)
        return True

    def save_note(self, qid: str, text: str) -> None:
        p = self.load()
        if text.strip():
            p["notes"][qid] = text
        else:
            p["notes"].pop(qid, None)
        self._save(p)

    def record_simulado_answers(self, answers: dict[str, dict[str, Any]]) -> None:
        p = self.load()
        ts = datetime.now(timezone.utc).isoformat()
        for qid, ans in answers.items():
            p["simulado_answers"][qid] = {
                "chosen": ans["chosen"],
                "correct": ans["correct"],
                "ts": ts,
            }
        self._save(p)

    def record_session(self, score: int, total: int, modo: str, duration_s: float) -> None:
        p = self.load()
        p["sessions"].append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "score": score,
                "total": total,
                "modo": modo,
                "duration_s": duration_s,
            }
        )
        self._save(p)


# ============================================================
# Backend 2: Supabase (sem auth, single-user)
# ============================================================


class SupabaseBackend:
    name = "supabase"

    def __init__(self, url: str, anon_key: str):
        from supabase import create_client

        self._client = create_client(url, anon_key)

    def load(self) -> dict[str, Any]:
        try:
            ans = self._client.table("answers").select("*").execute().data or []
            bms = self._client.table("bookmarks").select("question_id").execute().data or []
            nts = self._client.table("notes").select("*").execute().data or []
            sss = self._client.table("sessions").select("*").order("ts", desc=True).execute().data or []
            try:
                sim_ans = self._client.table("simulado_answers").select("*").execute().data or []
            except Exception:
                sim_ans = []
        except Exception as e:
            print(f"[progress] Supabase load falhou: {e}")
            return _empty_state()

        return {
            "answers": {
                a["question_id"]: {
                    "chosen": a["chosen"],
                    "correct": a["correct"],
                    "ts": a["ts"],
                    "confianca": a.get("confianca", ""),
                }
                for a in ans
            },
            "simulado_answers": {
                a["question_id"]: {
                    "chosen": a["chosen"],
                    "correct": a["correct"],
                    "ts": a["ts"],
                }
                for a in sim_ans
            },
            "bookmarked": [b["question_id"] for b in bms],
            "notes": {n["question_id"]: n["conteudo"] for n in nts},
            "sessions": [
                {
                    "ts": s["ts"],
                    "score": s["score"],
                    "total": s["total"],
                    "modo": s["modo"],
                    "duration_s": s["duration_s"],
                }
                for s in sss
            ],
        }

    def record_answer(self, qid: str, chosen: str, correct: bool, confianca: str = "") -> None:
        try:
            self._client.table("answers").upsert({
                "question_id": qid,
                "chosen": chosen,
                "correct": correct,
                "confianca": confianca,
                "ts": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception as e:
            print(f"[progress] record_answer falhou: {e}")

    def toggle_bookmark(self, qid: str) -> bool:
        try:
            existing = (
                self._client.table("bookmarks")
                .select("question_id")
                .eq("question_id", qid)
                .execute()
                .data
            )
            if existing:
                self._client.table("bookmarks").delete().eq("question_id", qid).execute()
                return False
            self._client.table("bookmarks").insert({"question_id": qid}).execute()
            return True
        except Exception as e:
            print(f"[progress] toggle_bookmark falhou: {e}")
            return False

    def save_note(self, qid: str, text: str) -> None:
        try:
            if text.strip():
                self._client.table("notes").upsert({
                    "question_id": qid,
                    "conteudo": text,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
            else:
                self._client.table("notes").delete().eq("question_id", qid).execute()
        except Exception as e:
            print(f"[progress] save_note falhou: {e}")

    def record_simulado_answers(self, answers: dict[str, dict[str, Any]]) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        for qid, ans in answers.items():
            try:
                self._client.table("simulado_answers").upsert({
                    "question_id": qid,
                    "chosen": ans["chosen"],
                    "correct": ans["correct"],
                    "ts": ts,
                }).execute()
            except Exception as e:
                print(f"[progress] record_simulado_answers falhou para {qid}: {e}")

    def record_session(self, score: int, total: int, modo: str, duration_s: float) -> None:
        try:
            self._client.table("sessions").insert({
                "score": score,
                "total": total,
                "modo": modo,
                "duration_s": duration_s,
            }).execute()
        except Exception as e:
            print(f"[progress] record_session falhou: {e}")


# ============================================================
# Seleção de backend (cached)
# ============================================================


def _get_credentials() -> tuple[str | None, str | None]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    try:
        import streamlit as st
        if not url:
            url = st.secrets.get("SUPABASE_URL")  # type: ignore[attr-defined]
        if not key:
            key = st.secrets.get("SUPABASE_ANON_KEY")  # type: ignore[attr-defined]
    except Exception:
        pass
    return url, key


_BACKEND: ProgressBackend | None = None


def get_backend() -> ProgressBackend:
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND
    url, key = _get_credentials()
    if url and key:
        try:
            _BACKEND = SupabaseBackend(url, key)
            return _BACKEND
        except Exception as e:
            print(f"[progress] Falha ao inicializar Supabase ({e}); caindo pra JSON local.")
    _BACKEND = JSONBackend()
    return _BACKEND


# ============================================================
# API pública
# ============================================================


def load_progress() -> dict[str, Any]:
    return get_backend().load()


def record_answer(qid: str, chosen: str, correct: bool, confianca: str = "") -> None:
    get_backend().record_answer(qid, chosen, correct, confianca)


def toggle_bookmark(qid: str) -> bool:
    return get_backend().toggle_bookmark(qid)


def save_note(qid: str, text: str) -> None:
    get_backend().save_note(qid, text)


def record_simulado_answers(answers: dict[str, dict[str, Any]]) -> None:
    get_backend().record_simulado_answers(answers)


def record_session(score: int, total: int, modo: str, duration_s: float) -> None:
    get_backend().record_session(score, total, modo, duration_s)


def save_progress(_data: dict[str, Any]) -> None:
    """Compat: backend antigo expunha save_progress(). Hoje cada operação salva sozinha."""
    return
