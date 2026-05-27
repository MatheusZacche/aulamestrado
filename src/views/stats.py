"""Estatísticas — métricas separadas de estudo e simulado."""
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

    study_answers = progress.get("answers", {})
    sim_answers = progress.get("simulado_answers", {})
    sessions = [s for s in progress.get("sessions", []) if s.get("modo") == "simulado"]

    if not study_answers and not sim_answers and not sessions:
        st.info("Você ainda não respondeu nenhuma questão. Vai pra aba **Estudar** ou **Simulado**.")
        return

    qmap = {q.id: q for q in bank.questions}

    tab_estudo, tab_simulado = st.tabs(["Modo Estudo", "Simulados"])

    # ==================== ABA ESTUDO ====================
    with tab_estudo:
        if not study_answers:
            st.info("Nenhuma questão respondida no modo Estudo ainda.")
        else:
            total = len(study_answers)
            acertos = sum(1 for a in study_answers.values() if a.get("correct"))

            c1, c2, c3 = st.columns(3)
            c1.metric("Estudadas", total)
            c2.metric("Acertos", acertos)
            c3.metric("Aproveitamento", f"{100 * acertos / total:.0f}%" if total else "—")

            st.divider()

            st.subheader("Desempenho por eixo")
            rows = []
            for eixo_key, eixo_data in topics["eixos"].items():
                qs_eixo = [qid for qid in study_answers if qid in qmap and qmap[qid].eixo == eixo_key]
                if not qs_eixo:
                    continue
                n = len(qs_eixo)
                ac = sum(1 for qid in qs_eixo if study_answers[qid].get("correct"))
                rows.append({
                    "Eixo": eixo_data["label"],
                    "Respondidas": n,
                    "Acertos": ac,
                    "Aproveitamento": f"{100 * ac / n:.0f}%",
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.subheader("Onde você mais erra (estudo)")
            _render_error_heatmap(study_answers, qmap)

    # ==================== ABA SIMULADO ====================
    with tab_simulado:
        if not sessions and not sim_answers:
            st.info("Nenhum simulado realizado ainda.")
        else:
            if sessions:
                st.subheader("Histórico de simulados")
                df_sim = pd.DataFrame([
                    {
                        "Data": s["ts"][:16].replace("T", " "),
                        "Acertos": s["score"],
                        "Total": s["total"],
                        "%": f"{100 * s['score'] / s['total']:.0f}%" if s["total"] else "—",
                        "Duração (min)": f"{s['duration_s'] / 60:.0f}",
                    }
                    for s in sessions
                ])
                st.dataframe(df_sim, use_container_width=True, hide_index=True)

                st.divider()

            if sim_answers:
                total_sim = len(sim_answers)
                acertos_sim = sum(1 for a in sim_answers.values() if a.get("correct"))

                c1, c2, c3 = st.columns(3)
                c1.metric("Questões vistas", total_sim)
                c2.metric("Acertos", acertos_sim)
                c3.metric("Aproveitamento", f"{100 * acertos_sim / total_sim:.0f}%" if total_sim else "—")

                st.divider()

                st.subheader("Desempenho por eixo (simulados)")
                rows = []
                for eixo_key, eixo_data in topics["eixos"].items():
                    qs_eixo = [qid for qid in sim_answers if qid in qmap and qmap[qid].eixo == eixo_key]
                    if not qs_eixo:
                        continue
                    n = len(qs_eixo)
                    ac = sum(1 for qid in qs_eixo if sim_answers[qid].get("correct"))
                    rows.append({
                        "Eixo": eixo_data["label"],
                        "Respondidas": n,
                        "Acertos": ac,
                        "Aproveitamento": f"{100 * ac / n:.0f}%",
                    })
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                st.subheader("Onde você mais erra (simulados)")
                _render_error_heatmap(sim_answers, qmap)


def _render_error_heatmap(answers: dict, qmap: dict) -> None:
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
                "Taxa de erro": f"{100 * erros_por_sub[s] / total_por_sub[s]:.0f}%",
            }
            for s in total_por_sub
            if total_por_sub[s] >= 2 and erros_por_sub[s] > 0
        ]
        rows_sub.sort(key=lambda r: -erros_por_sub[r["Subtópico"]])
        if rows_sub:
            st.dataframe(pd.DataFrame(rows_sub), use_container_width=True, hide_index=True)
        else:
            st.caption("Sem dados suficientes ou você não errou nenhuma com subtópico definido.")
