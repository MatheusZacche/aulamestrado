"""Estatísticas — visão enxuta sem calibração ('chutei/certeza')."""
from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from src.data.load import load_bank, load_topics
from src.data.progress import load_progress


def render() -> None:
    bank = load_bank()
    topics = load_topics()
    progress = load_progress()

    answers = progress.get("answers", {})
    if not answers:
        st.info("Você ainda não respondeu nenhuma questão. Vai pra aba **Estudar**.")
        return

    qmap = {q.id: q for q in bank.questions}

    # ---------- Visão geral ----------
    total = len(answers)
    acertos = sum(1 for a in answers.values() if a.get("correct"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Respondidas", total)
    c2.metric("Acertos", acertos)
    c3.metric("Aproveitamento", f"{100*acertos/total:.0f}%" if total else "—")

    st.divider()

    # ---------- Por eixo ----------
    st.subheader("Desempenho por eixo")
    rows = []
    for eixo_key, eixo_data in topics["eixos"].items():
        qs_eixo = [qid for qid in answers if qid in qmap and qmap[qid].eixo == eixo_key]
        if not qs_eixo:
            continue
        n = len(qs_eixo)
        ac = sum(1 for qid in qs_eixo if answers[qid].get("correct"))
        rows.append({
            "Eixo": eixo_data["label"],
            "Respondidas": n,
            "Acertos": ac,
            "Aproveitamento": f"{100*ac/n:.0f}%",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ---------- Onde mais erra (por subtópico) ----------
    st.subheader("Onde você mais erra")
    erros_por_sub: Counter = Counter()
    total_por_sub: Counter = Counter()
    for qid, a in answers.items():
        q = qmap.get(qid)
        if not q:
            continue
        for s in q.subtopicos or ["(sem subtópico)"]:
            total_por_sub[s] += 1
            if not a.get("correct"):
                erros_por_sub[s] += 1

    if total_por_sub:
        rows_sub = [
            {
                "Subtópico": s,
                "Erros": erros_por_sub[s],
                "Total": total_por_sub[s],
                "Taxa de erro": f"{100*erros_por_sub[s]/total_por_sub[s]:.0f}%",
            }
            for s in total_por_sub
            if total_por_sub[s] >= 2 and erros_por_sub[s] > 0
        ]
        rows_sub.sort(key=lambda r: -erros_por_sub[r["Subtópico"]])
        if rows_sub:
            st.dataframe(pd.DataFrame(rows_sub), use_container_width=True, hide_index=True)
        else:
            st.caption("Sem dados suficientes ou você não errou nenhuma com subtópico definido.")

    st.divider()

    # ---------- Histórico de simulados ----------
    st.subheader("Histórico de simulados")
    sims = [s for s in progress.get("sessions", []) if s.get("modo") == "simulado"]
    if sims:
        df_sim = pd.DataFrame([
            {
                "Data": s["ts"][:16].replace("T", " "),
                "Acertos": s["score"],
                "Total": s["total"],
                "%": f"{100*s['score']/s['total']:.0f}%" if s["total"] else "—",
                "Duração (min)": f"{s['duration_s']/60:.0f}",
            }
            for s in sims
        ])
        st.dataframe(df_sim, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhum simulado completo ainda.")
