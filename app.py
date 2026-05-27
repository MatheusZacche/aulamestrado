"""Aulamestrado — Home.

Streamlit multipage app para preparação da prova do mestrado PPGI/UFES.
Rode: streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from src.data.load import load_bank, load_topics
from src.data.progress import load_progress

st.set_page_config(
    page_title="Aulamestrado — PPGI UFES",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Aulamestrado")
st.caption("Banco de questões e simulados — Mestrado PPGI/UFES")

bank = load_bank()
progress = load_progress()
topics = load_topics()

total_q = len(bank.questions)
respondidas = len(progress.get("answers", {}))
acertos = sum(1 for a in progress.get("answers", {}).values() if a.get("correct"))
oficiais = sum(1 for q in bank.questions if q.origem.value == "oficial")
geradas = total_q - oficiais
validadas = sum(1 for q in bank.questions if q.validacao.validado and q.validacao.confianca >= 0.8)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Questões no banco", total_q, help=f"{oficiais} oficiais + {geradas} geradas")
c2.metric("Validadas (≥0.8)", validadas, help="Aprovadas pelo agente validador com alta confiança")
c3.metric("Você respondeu", respondidas)
c4.metric("Acertos", f"{acertos}/{respondidas}" if respondidas else "—",
          delta=f"{100*acertos/respondidas:.0f}%" if respondidas else None)

st.divider()

st.subheader("Conteúdo programático oficial")
st.caption("Edital PPGI 03/2026 — Mestrado em Informática UFES")

cols = st.columns(2)
for i, (key, eixo) in enumerate(topics["eixos"].items()):
    with cols[i % 2]:
        n = sum(1 for q in bank.questions if q.eixo == key)
        st.markdown(f"### {eixo['label']}")
        st.caption(f"{n} questão(ões) no banco")
        with st.expander("Bibliografia oficial"):
            for b in eixo["bibliografia"]:
                st.markdown(f"- {b}")

st.divider()

st.subheader("Por onde começar")
st.markdown(
    """
- **📚 Estudar** — uma questão por vez, com feedback imediato e explicação por alternativa.
- **📝 Simulado** — 20 questões cronometradas (2h), sem feedback até o fim. Replica o dia da prova.
- **📊 Estatísticas** — sua evolução por eixo e tópico.
- **🔖 Salvas** — questões marcadas para revisar.
"""
)

if validadas == 0 and total_q > 0:
    st.warning(
        "⚠️ Nenhuma questão validada semanticamente ainda. As explicações por alternativa "
        "estarão vazias até o agente validador rodar:\n\n"
        "```\npython -m src.agents.validator --all\n```\n"
        "(requer `ANTHROPIC_API_KEY` no `.env`)"
    )

st.caption("Provas oficiais publicadas pelo PPGI/UFES estão em `data/exams/raw/`.")
