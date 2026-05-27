"""Estatísticas de progresso pessoal."""
from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from src.data.load import load_bank, load_topics
from src.data.progress import load_progress

st.set_page_config(page_title="Estatísticas — Aulamestrado", page_icon="📊", layout="wide")
st.title("📊 Estatísticas")

bank = load_bank()
topics = load_topics()
progress = load_progress()

answers = progress.get("answers", {})
if not answers:
    st.info("Você ainda não respondeu nenhuma questão. Comece pelo modo Estudar.")
    st.stop()

# Map question_id -> Question
qmap = {q.id: q for q in bank.questions}

# ---------- Visão geral ----------
total = len(answers)
acertos = sum(1 for a in answers.values() if a.get("correct"))
chutados = sum(1 for a in answers.values() if a.get("confianca") == "Chutei")
certezas = sum(1 for a in answers.values() if a.get("confianca") == "Tenho certeza")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total respondidas", total)
c2.metric("Acertos", f"{acertos} ({100*acertos/total:.0f}%)")
c3.metric("Chutados", chutados)
c4.metric("Com certeza", certezas)

# Calibração: dos "chutei" quantos acertou; dos "tenho certeza" quantos errou
if chutados:
    chutados_certos = sum(
        1 for a in answers.values() if a.get("confianca") == "Chutei" and a.get("correct")
    )
    st.caption(f"📈 Calibração: dos {chutados} que você chutou, acertou {chutados_certos} ({100*chutados_certos/chutados:.0f}%). "
               "Se este número está alto, você sabe mais do que pensa.")
if certezas:
    erros_com_certeza = sum(
        1 for a in answers.values() if a.get("confianca") == "Tenho certeza" and not a.get("correct")
    )
    if erros_com_certeza:
        st.caption(f"⚠️ Você errou {erros_com_certeza} questão(ões) marcando 'tenho certeza' — revisar prioritariamente.")

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
    rows.append(
        {
            "Eixo": eixo_data["label"],
            "Respondidas": n,
            "Acertos": ac,
            "Aproveitamento": f"{100*ac/n:.0f}%",
        }
    )
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- Por subtópico (top fraquezas) ----------
st.subheader("Onde você mais erra (por subtópico)")
erros_por_sub: Counter = Counter()
total_por_sub: Counter = Counter()
for qid, a in answers.items():
    q = qmap.get(qid)
    if not q:
        continue
    for s in q.subtopicos or ["sem_subtopico"]:
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
        if total_por_sub[s] >= 2
    ]
    rows_sub.sort(key=lambda r: -erros_por_sub[r["Subtópico"]])
    if rows_sub:
        st.dataframe(pd.DataFrame(rows_sub), use_container_width=True, hide_index=True)
    else:
        st.caption("Ainda não há dados suficientes para subtópicos (mín. 2 questões por subtópico).")

st.divider()

# ---------- Histórico de simulados ----------
st.subheader("Histórico de simulados")
sessoes = progress.get("sessions", [])
sims = [s for s in sessoes if s.get("modo") == "simulado"]
if sims:
    df_sim = pd.DataFrame(
        [
            {
                "Data": s["ts"][:16].replace("T", " "),
                "Acertos": s["score"],
                "Total": s["total"],
                "%": f"{100*s['score']/s['total']:.0f}%" if s["total"] else "—",
                "Duração (min)": f"{s['duration_s']/60:.0f}",
            }
            for s in sims
        ]
    )
    st.dataframe(df_sim, use_container_width=True, hide_index=True)
else:
    st.caption("Nenhum simulado completo ainda.")
