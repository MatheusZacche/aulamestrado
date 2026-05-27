"""Componentes Streamlit reutilizáveis."""
from __future__ import annotations

import streamlit as st

from src.data.schema import Question


def render_alternativas_radio(q: Question, key: str) -> str | None:
    """Mostra alternativas como radio. Retorna a chave escolhida ou None."""
    opcoes = [f"{a.chave}) {a.texto}" for a in q.alternativas]
    escolha = st.radio("Sua resposta:", options=opcoes, index=None, key=key)
    if escolha is None:
        return None
    return escolha.split(")", 1)[0].strip().lower()


def render_feedback(q: Question, chosen: str) -> None:
    """Mostra se acertou + explicações por alternativa."""
    acertou = chosen == q.gabarito
    if q.anulada:
        st.warning(f"⚠️ Questão anulada pela banca: {q.motivo_anulacao}")
    elif acertou:
        st.success(f"✅ Correto! Gabarito: **{q.gabarito.upper()}**")
    else:
        st.error(f"❌ Errado. Você marcou **{chosen.upper()}** — gabarito é **{q.gabarito.upper()}**")

    st.markdown("**Explicações:**")
    for a in q.alternativas:
        is_correct = a.chave == q.gabarito
        is_chosen = a.chave == chosen
        icon = "✅" if is_correct else "❌"
        marker = " 👈 sua resposta" if is_chosen and not is_correct else ""
        with st.expander(f"{icon} {a.chave.upper()}) {a.texto[:80]}{'...' if len(a.texto) > 80 else ''}{marker}"):
            if a.explicacao:
                st.write(a.explicacao)
            else:
                st.caption("_Explicação ainda não gerada. Rode o agente validador com `--all` (semântico) para preencher._")


def render_metadata_badge(q: Question) -> None:
    """Badges com metadados da questão."""
    cols = st.columns(4)
    cols[0].markdown(f"**Origem:** `{q.origem.value}`")
    cols[1].markdown(f"**Eixo:** `{q.eixo}`")
    if q.ano:
        cols[2].markdown(f"**Ano:** `{q.ano}` (Q{q.numero_na_prova:02d})")
    else:
        cols[2].markdown("**Ano:** —")
    cols[3].markdown(f"**Dificuldade:** `{q.dificuldade.value}`")
    if q.subtopicos:
        st.caption("Subtópicos: " + ", ".join(f"`{s}`" for s in q.subtopicos))
    if q.validacao.validado:
        cor = "🟢" if q.validacao.confianca >= 0.8 else ("🟡" if q.validacao.confianca >= 0.5 else "🔴")
        st.caption(f"{cor} Validação: confiança {q.validacao.confianca:.2f}")
        if q.validacao.flags:
            st.caption("Flags: " + ", ".join(f"`{f}`" for f in q.validacao.flags))
    else:
        st.caption("⚪ Não validada semanticamente")
