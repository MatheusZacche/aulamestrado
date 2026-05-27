"""Modo Estudo — uma questão por vez, feedback imediato.

Filtros simplificados: apenas Eixo + toggle "incluir já respondidas".
Default: pula questões já respondidas (avança pra próxima nova).
"""
from __future__ import annotations

import random

import streamlit as st

from src.data.load import load_bank, load_topics
from src.data.progress import load_progress, record_answer
from src.ui.components import (
    render_alternativas_radio,
    render_enunciado,
    render_feedback,
)


def render() -> None:
    bank = load_bank()
    topics = load_topics()
    progress = load_progress()

    # ---------- Filtros enxutos ----------
    f1, f2 = st.columns([2, 1])
    eixo = f1.selectbox(
        "Eixo",
        options=["todos"] + list(topics["eixos"].keys()),
        format_func=lambda k: "Todos os eixos" if k == "todos" else topics["eixos"][k]["label"],
        key="study_eixo",
    )
    incluir_respondidas = f2.toggle(
        "Incluir respondidas",
        value=False,
        help="Por padrão, mostra apenas questões que você ainda não respondeu.",
        key="study_incluir_resp",
    )

    respondidas_ids = set(progress["answers"].keys())

    def matches(q) -> bool:
        if eixo != "todos" and q.eixo != eixo:
            return False
        if q.anulada:
            return False  # sempre pula anuladas
        if not incluir_respondidas and q.id in respondidas_ids:
            return False
        return True

    candidatos = [q for q in bank.questions if matches(q)]

    if not candidatos:
        if not incluir_respondidas and respondidas_ids:
            st.success(
                "🎉 Você respondeu todas as questões deste filtro. "
                "Ative **Incluir respondidas** para revisar."
            )
        else:
            st.warning("Nenhuma questão neste filtro.")
        return

    # ---------- Índice atual ----------
    state_idx_key = "study_idx"
    state_ids_key = "study_ids"

    ids_atuais = [q.id for q in candidatos]
    if state_ids_key not in st.session_state or st.session_state[state_ids_key] != ids_atuais:
        st.session_state[state_ids_key] = ids_atuais
        st.session_state[state_idx_key] = 0

    idx = st.session_state.get(state_idx_key, 0) % len(candidatos)
    q = next(qq for qq in candidatos if qq.id == ids_atuais[idx])

    # ---------- Navegação ----------
    nav1, nav2, nav3, info = st.columns([1, 1, 1, 3])
    if nav1.button("⬅️ Anterior", key="study_prev"):
        st.session_state[state_idx_key] = (idx - 1) % len(candidatos)
        st.rerun()
    if nav2.button("Próxima ➡️", key="study_next"):
        st.session_state[state_idx_key] = (idx + 1) % len(candidatos)
        st.rerun()
    if nav3.button("🎲 Aleatória", key="study_random"):
        st.session_state[state_idx_key] = random.randrange(len(candidatos))
        st.rerun()
    info.markdown(f"**{idx + 1} de {len(candidatos)}** · `{q.id}` · eixo: `{q.eixo}` · {q.dificuldade.value}")

    st.divider()

    # ---------- Enunciado + alternativas ----------
    st.markdown("### Enunciado")
    render_enunciado(q.enunciado, question=q)

    state_key = f"chosen_{q.id}"
    shown_key = f"shown_{q.id}"

    chosen = render_alternativas_radio(q, key=state_key)

    if st.button("Ver gabarito e explicação", type="primary", disabled=chosen is None, key=f"reveal_{q.id}"):
        st.session_state[shown_key] = True

    if st.session_state.get(shown_key) and chosen:
        correct = (chosen == q.gabarito) and not q.anulada
        record_answer(q.id, chosen, correct)
        render_feedback(q, chosen)
        if st.button("Próxima questão ➡️", type="primary", key=f"after_{q.id}"):
            # avança e limpa estado da questão atual
            st.session_state.pop(shown_key, None)
            st.session_state.pop(state_key, None)
            st.session_state[state_idx_key] = (idx + 1) % len(candidatos)
            st.rerun()
