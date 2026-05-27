"""Questões marcadas para revisar + erradas anteriormente."""
from __future__ import annotations

import streamlit as st

from src.data.load import load_bank
from src.data.progress import load_progress, toggle_bookmark
from src.ui.components import (
    render_alternativas_radio,
    render_enunciado,
    render_feedback,
    render_metadata_badge,
)

st.set_page_config(page_title="Salvas — Aulamestrado", page_icon="🔖", layout="wide")
st.title("🔖 Minhas questões salvas")

bank = load_bank()
progress = load_progress()
qmap = {q.id: q for q in bank.questions}

tab1, tab2 = st.tabs([f"🔖 Marcadas ({len(progress['bookmarked'])})", "❌ Erradas anteriormente"])

with tab1:
    if not progress["bookmarked"]:
        st.info("Você ainda não marcou nenhuma questão. No modo Estudar, clique em 🔖 Marcar para revisar.")
    for qid in progress["bookmarked"]:
        q = qmap.get(qid)
        if not q:
            continue
        with st.expander(f"`{q.id}` — {q.enunciado[:100]}..."):
            render_metadata_badge(q)
            render_enunciado(q.enunciado)
            for a in q.alternativas:
                mark = " ✅" if a.chave == q.gabarito else ""
                st.markdown(f"**{a.chave.upper()})** {a.texto}{mark}")
                if a.explicacao:
                    st.caption(a.explicacao)
            if st.button("Remover marcação", key=f"rm_{qid}"):
                toggle_bookmark(qid)
                st.rerun()

with tab2:
    erradas = [
        qid
        for qid, a in progress["answers"].items()
        if not a.get("correct") and qid in qmap
    ]
    if not erradas:
        st.info("Nada por aqui — você não errou nenhuma questão (ou ainda não respondeu).")
    for qid in erradas:
        q = qmap[qid]
        chosen = progress["answers"][qid]["chosen"]
        with st.expander(f"`{q.id}` — você marcou {chosen.upper()}, gabarito é {q.gabarito.upper()}"):
            render_metadata_badge(q)
            render_enunciado(q.enunciado)
            render_feedback(q, chosen)
