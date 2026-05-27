"""Modo Estudo — uma questão por vez com feedback imediato.

Filtros: eixo, ano, dificuldade, origem, somente não-respondidas, somente erradas anteriormente.
"""
from __future__ import annotations

import random

import streamlit as st

from src.data.load import load_bank, load_topics
from src.data.progress import (
    load_progress,
    record_answer,
    save_note,
    toggle_bookmark,
)
from src.ui.components import render_alternativas_radio, render_feedback, render_metadata_badge

st.set_page_config(page_title="Estudar — Aulamestrado", page_icon="📚", layout="wide")
st.title("📚 Modo Estudo")

bank = load_bank()
topics = load_topics()
progress = load_progress()

# ---------- Filtros ----------
with st.sidebar:
    st.header("Filtros")
    eixo = st.selectbox(
        "Eixo",
        options=["todos"] + list(topics["eixos"].keys()),
        format_func=lambda k: "Todos" if k == "todos" else topics["eixos"][k]["label"],
    )
    anos_disponiveis = sorted({q.ano for q in bank.questions if q.ano})
    ano = st.selectbox("Ano da prova", options=["todos", *anos_disponiveis, "geradas"])
    dificuldade = st.selectbox("Dificuldade", options=["todas", "facil", "medio", "dificil"])
    confianca_min = st.slider("Confiança mínima da validação", 0.0, 1.0, 0.0, step=0.1)
    apenas_nao_respondidas = st.checkbox("Apenas não respondidas")
    apenas_erradas = st.checkbox("Apenas erradas anteriormente")
    pular_anuladas = st.checkbox("Pular questões anuladas", value=True)


def matches(q) -> bool:
    if eixo != "todos" and q.eixo != eixo:
        return False
    if ano == "geradas":
        if q.origem.value == "oficial":
            return False
    elif ano != "todos" and q.ano != ano:
        return False
    if dificuldade != "todas" and q.dificuldade.value != dificuldade:
        return False
    if q.validacao.confianca < confianca_min and q.origem.value != "oficial":
        return False
    if pular_anuladas and q.anulada:
        return False
    ans = progress["answers"].get(q.id)
    if apenas_nao_respondidas and ans is not None:
        return False
    if apenas_erradas and (ans is None or ans.get("correct")):
        return False
    return True


candidatos = [q for q in bank.questions if matches(q)]

if not candidatos:
    st.warning("Nenhuma questão bate com esses filtros.")
    st.stop()

# ---------- Seleção da questão atual ----------
if "estudar_idx" not in st.session_state:
    st.session_state.estudar_idx = 0
    st.session_state.estudar_ids = [q.id for q in candidatos]

# Resincroniza se filtros mudaram
ids_atuais = [q.id for q in candidatos]
if st.session_state.estudar_ids != ids_atuais:
    st.session_state.estudar_ids = ids_atuais
    st.session_state.estudar_idx = 0

idx = st.session_state.estudar_idx % len(candidatos)
q = next(qq for qq in candidatos if qq.id == st.session_state.estudar_ids[idx])

# ---------- Navegação ----------
nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 3])
if nav1.button("⬅️ Anterior"):
    st.session_state.estudar_idx = (idx - 1) % len(candidatos)
    st.rerun()
if nav2.button("Próxima ➡️"):
    st.session_state.estudar_idx = (idx + 1) % len(candidatos)
    st.rerun()
if nav3.button("🎲 Aleatória"):
    st.session_state.estudar_idx = random.randrange(len(candidatos))
    st.rerun()
nav4.markdown(f"**{idx + 1} de {len(candidatos)}** • `{q.id}`")

st.divider()

# ---------- Conteúdo da questão ----------
render_metadata_badge(q)
st.markdown("### Enunciado")
st.markdown(q.enunciado)

state_key = f"chosen_{q.id}"
shown_key = f"shown_{q.id}"

chosen = render_alternativas_radio(q, key=state_key)

col_conf, col_act = st.columns([2, 1])
with col_conf:
    confianca = st.radio(
        "Antes de ver o gabarito:",
        options=["", "Chutei", "Tenho certeza"],
        index=0,
        horizontal=True,
        key=f"confianca_{q.id}",
    )

with col_act:
    bookmarked = q.id in progress["bookmarked"]
    if st.button(("🔖 Remover marcação" if bookmarked else "🔖 Marcar para revisar"), key=f"bm_{q.id}"):
        toggle_bookmark(q.id)
        st.rerun()

if st.button("Ver gabarito e explicação", type="primary", disabled=chosen is None, key=f"reveal_{q.id}"):
    st.session_state[shown_key] = True

if st.session_state.get(shown_key) and chosen:
    correct = (chosen == q.gabarito) and not q.anulada
    record_answer(q.id, chosen, correct, confianca)
    render_feedback(q, chosen)

# ---------- Notas ----------
st.divider()
with st.expander("📝 Minhas anotações"):
    nota = st.text_area(
        "Anotações pessoais (salvas localmente):",
        value=progress["notes"].get(q.id, ""),
        key=f"nota_{q.id}",
        height=120,
    )
    if st.button("Salvar anotação", key=f"save_nota_{q.id}"):
        save_note(q.id, nota)
        st.success("Anotação salva.")
