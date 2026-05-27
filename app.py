"""Aulamestrado — entrypoint Streamlit (single-page com tabs no topo).

Rode: streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from src.data.progress import get_backend
from src.views import simulado, stats, study

st.set_page_config(
    page_title="Aulamestrado — PPGI UFES",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Cabeçalho ----------
header_cols = st.columns([6, 1])
header_cols[0].title("🎓 Aulamestrado")
header_cols[0].caption("Banco de questões — Mestrado PPGI/UFES")

backend_name = get_backend().name
header_cols[1].markdown(
    "<div style='text-align:right; padding-top:1rem;'>"
    + ("☁️ Nuvem" if backend_name == "supabase" else "💾 Local")
    + "</div>",
    unsafe_allow_html=True,
)

# ---------- Tabs no topo ----------
tab_estudar, tab_simulado, tab_stats = st.tabs(
    ["📚 Estudar", "📝 Simulado", "📊 Estatísticas"]
)

with tab_estudar:
    study.render()

with tab_simulado:
    simulado.render()

with tab_stats:
    stats.render()
