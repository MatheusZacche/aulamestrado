"""Modo Simulado — 20 questões, 2 horas, sem feedback até o fim."""
from __future__ import annotations

import random
import time

import streamlit as st

from src.data.load import load_bank
from src.data.progress import record_session
from src.data.schema import Question
from src.ui.components import render_enunciado

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False


TEMPO_LIMITE_S = 2 * 60 * 60  # 2 horas


def gerar_simulado(seed: int | None = None) -> list[Question]:
    """20 questões distribuídas pelos 4 eixos. Prioriza oficiais e alta-confiança."""
    bank = load_bank()
    rnd = random.Random(seed)
    eixos = ["raciocinio_logico", "programacao", "paradigmas", "estruturas_dados"]
    selecionadas: list[Question] = []
    for e in eixos:
        pool = [q for q in bank.questions if q.eixo == e and not q.anulada]

        def prio(q: Question) -> tuple[int, float]:
            origem = 0 if q.origem.value == "oficial" else 1
            return (origem, -q.validacao.confianca)

        pool_sorted = sorted(pool, key=prio)
        rnd.shuffle(pool_sorted[:30])
        selecionadas.extend(pool_sorted[:5])

    if len(selecionadas) < 20:
        restantes = [q for q in bank.questions if q not in selecionadas and not q.anulada]
        rnd.shuffle(restantes)
        selecionadas.extend(restantes[: 20 - len(selecionadas)])
    return selecionadas[:20]


def render() -> None:
    st.caption("20 questões · 2 horas · mínimo 60% para aprovação")

    if "sim_iniciado" not in st.session_state:
        st.session_state.sim_iniciado = False

    if not st.session_state.sim_iniciado:
        seed = st.text_input(
            "Seed opcional (mesma seed = mesmo simulado, útil pra refazer)",
            value="",
            key="sim_seed_input",
        )
        if st.button("Iniciar simulado", type="primary", key="sim_start"):
            s = int(seed) if seed.isdigit() else None
            st.session_state.sim_questoes = gerar_simulado(s)
            st.session_state.sim_respostas = {}
            st.session_state.sim_inicio = time.time()
            st.session_state.sim_iniciado = True
            st.session_state.sim_finalizado = False
            st.rerun()
        return

    questoes: list[Question] = st.session_state.sim_questoes
    respostas: dict[str, str] = st.session_state.sim_respostas
    inicio: float = st.session_state.sim_inicio

    decorrido = time.time() - inicio
    restante = max(0, TEMPO_LIMITE_S - decorrido)
    tempo_esgotado = restante <= 0

    if not st.session_state.get("sim_finalizado") and tempo_esgotado:
        st.session_state.sim_finalizado = True

    # ---------- Resultado final ----------
    if st.session_state.get("sim_finalizado"):
        acertos = sum(
            1 for q in questoes
            if (respostas.get(q.id) == q.gabarito) and not q.anulada
        )
        total_validas = sum(1 for q in questoes if not q.anulada)
        pct = 100 * acertos / total_validas if total_validas else 0
        aprovado = pct >= 60

        st.header("Resultado")
        c1, c2, c3 = st.columns(3)
        c1.metric("Acertos", f"{acertos} / {total_validas}")
        c2.metric("Aproveitamento", f"{pct:.1f}%")
        c3.metric(
            "Status",
            "✅ APROVADO" if aprovado else "❌ ELIMINADO",
            help="Corte oficial: 60% (24 de 40 pontos)",
        )

        if not st.session_state.get("sim_registrado"):
            record_session(acertos, total_validas, "simulado", time.time() - inicio)
            st.session_state.sim_registrado = True

        st.divider()
        st.subheader("Revisão por questão")
        for i, q in enumerate(questoes, 1):
            chosen = respostas.get(q.id, "")
            ok = chosen == q.gabarito and not q.anulada
            icon = "✅" if ok else ("⚪" if q.anulada else "❌")
            with st.expander(f"{icon} Q{i:02d} ({q.eixo}) — gabarito {q.gabarito.upper()}"):
                st.markdown(q.enunciado[:400] + ("..." if len(q.enunciado) > 400 else ""))
                for a in q.alternativas:
                    prefix = "👉 " if a.chave == chosen else "   "
                    mark = " ✅" if a.chave == q.gabarito else ""
                    st.markdown(f"{prefix}**{a.chave.upper()})** {a.texto[:120]}{mark}")
                if q.anulada:
                    st.caption(f"⚠️ Anulada: {q.motivo_anulacao}")
                elif not ok and chosen:
                    gab_alt = next(a for a in q.alternativas if a.chave == q.gabarito)
                    if gab_alt.explicacao:
                        st.info(f"**Por que {q.gabarito.upper()}:** {gab_alt.explicacao}")

        if st.button("Novo simulado", type="primary", key="sim_new"):
            for k in list(st.session_state.keys()):
                if k.startswith("sim_"):
                    del st.session_state[k]
            st.rerun()
        return

    # ---------- Cronômetro ----------
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=15_000, key="sim_timer_refresh")

    horas = int(restante // 3600)
    mins = int((restante % 3600) // 60)
    segs = int(restante % 60)

    c1, c2, c3 = st.columns([2, 2, 1])
    c1.metric("Tempo restante", f"{horas:02d}:{mins:02d}:{segs:02d}")
    c2.metric("Respondidas", f"{len(respostas)} / 20")
    if c3.button("Finalizar agora", key="sim_finalize"):
        st.session_state.sim_finalizado = True
        st.rerun()

    st.divider()

    # ---------- Navegação por questão ----------
    nav_cols = st.columns(20)
    if "sim_idx" not in st.session_state:
        st.session_state.sim_idx = 0
    for i in range(20):
        q_i = questoes[i]
        respondida = q_i.id in respostas
        label = f"{'✓' if respondida else '·'}{i + 1}"
        if nav_cols[i].button(label, key=f"sim_nav_{i}"):
            st.session_state.sim_idx = i
            st.rerun()

    idx = st.session_state.sim_idx
    q = questoes[idx]
    st.subheader(f"Questão {idx + 1} de 20")
    st.caption(f"`{q.id}` · eixo: {q.eixo}")
    render_enunciado(q.enunciado, question=q)

    opcoes = [f"{a.chave}) {a.texto}" for a in q.alternativas]
    default = None
    if q.id in respostas:
        chave_atual = respostas[q.id]
        for i_alt, a in enumerate(q.alternativas):
            if a.chave == chave_atual:
                default = i_alt
                break

    escolha = st.radio(
        "Resposta:",
        options=opcoes,
        index=default,
        key=f"sim_alt_{q.id}",
    )
    if escolha:
        chave = escolha.split(")", 1)[0].strip().lower()
        respostas[q.id] = chave

    cprev, cnext, _ = st.columns([1, 1, 4])
    if cprev.button("⬅️ Anterior", disabled=idx == 0, key="sim_prev_q"):
        st.session_state.sim_idx = max(0, idx - 1)
        st.rerun()
    if cnext.button("Próxima ➡️", disabled=idx == 19, key="sim_next_q"):
        st.session_state.sim_idx = min(19, idx + 1)
        st.rerun()
