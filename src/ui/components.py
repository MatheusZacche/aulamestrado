"""Componentes Streamlit reutilizáveis."""
from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from src.data.schema import Question

_IMAGES_DIR = Path(__file__).resolve().parents[2] / "data" / "exams" / "images"


# Marcadores típicos de código C em enunciados
_CODE_MARKERS = re.compile(
    r"(?m)^\s*(?:int|void|char|float|double|struct|return|printf|scanf|while|if|for|"
    r"#include|typedef|else|switch|case|break|continue)\b|"
    r"^\s*\{\s*$|^\s*\}\s*$|;\s*$"
)


def _split_text_and_code(text: str) -> list[tuple[str, str]]:
    """Heurística simples: detecta blocos contíguos de linhas com marcadores
    de código C e separa em segmentos [("text"|"code", conteudo), ...].

    Não é perfeito, mas evita renderizar código C dentro de markdown comum
    (que quebra indentação e símbolos como * e _).
    """
    lines = text.split("\n")
    segments: list[tuple[str, list[str]]] = []
    cur_kind: str | None = None
    cur_buf: list[str] = []

    def is_code_line(s: str) -> bool:
        return bool(_CODE_MARKERS.search(s))

    for line in lines:
        kind = "code" if is_code_line(line) else "text"
        # Heurística de continuidade: linha em branco mantém o tipo do bloco anterior
        if line.strip() == "" and cur_kind is not None:
            cur_buf.append(line)
            continue
        if cur_kind is None:
            cur_kind = kind
            cur_buf = [line]
        elif kind == cur_kind:
            cur_buf.append(line)
        else:
            segments.append((cur_kind, cur_buf))
            cur_kind = kind
            cur_buf = [line]
    if cur_buf and cur_kind is not None:
        segments.append((cur_kind, cur_buf))

    # Compacta blocos de código curtinhos (1 linha solta) de volta pra texto
    out: list[tuple[str, str]] = []
    for kind, buf in segments:
        content = "\n".join(buf).strip("\n")
        if kind == "code" and len(buf) < 2:
            # bloco "code" de uma linha só vira texto pra evitar falsos positivos
            out.append(("text", content))
        else:
            out.append((kind, content))
    # Merge segments consecutivos de mesmo tipo após compactação
    merged: list[tuple[str, str]] = []
    for kind, content in out:
        if merged and merged[-1][0] == kind:
            merged[-1] = (kind, merged[-1][1] + "\n" + content)
        else:
            merged.append((kind, content))
    return merged


_ITEM_START = re.compile(
    r"^(?:"
    r"[IVX]+\.\s"          # I. II. III. IV.
    r"|[ivx]+\)\s"         # i) ii) iii) iv)
    r"|\d+\.\s"            # 1. 2. 3.
    r"|[●•]\s"             # bullet points
    r"|\(\s?\)\s"          # ( ) V/F items
    r")",
)

_CLOSING_SENTENCE = re.compile(
    r"^(?:Assinale|Qual é|Qual das|Quais|Nessas condições|"
    r"Considerando as|É correto|Com base n[oa]s? (?:exposto|informações|texto)|"
    r"A partir d[oa]s?|De acordo|Marque|Indique)",
)


def _reflow_text(text: str) -> str:
    """Reflui texto extraído de PDF: junta linhas de continuação e separa
    itens estruturados (romanos, numerados, bullets) em parágrafos distintos.
    """
    lines = text.split("\n")
    paragraphs: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            paragraphs.append(" ".join(buf))
            buf.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue

        is_item = bool(_ITEM_START.match(stripped))
        starts_lower = stripped[0].islower() or stripped[0] in ",.;)"

        if is_item:
            flush()
            buf.append(stripped)
        elif starts_lower:
            buf.append(stripped)
        elif _CLOSING_SENTENCE.match(stripped) and paragraphs:
            flush()
            buf.append(stripped)
        elif buf and not _ITEM_START.match(buf[0]):
            buf.append(stripped)
        else:
            flush()
            buf.append(stripped)

    flush()

    parts: list[str] = []
    for p in paragraphs:
        if _ITEM_START.match(p):
            parts.append(f"**{p}**")
        else:
            parts.append(p)

    return "\n\n".join(parts)


def render_enunciado(enunciado: str, question: Question | None = None) -> None:
    """Renderiza enunciado tratando blocos de código C em monospace e
    refluindo texto de PDF para boa leitura."""
    segments = _split_text_and_code(enunciado)
    for kind, content in segments:
        if not content.strip():
            continue
        if kind == "code":
            st.code(content, language="c")
        else:
            st.markdown(_reflow_text(content))

    if question and question.tem_imagem:
        img_path = _IMAGES_DIR / f"{question.id}.png"
        if img_path.exists():
            st.image(str(img_path), caption="Figura da prova original")
        else:
            st.warning(
                "Esta questão contém uma figura/diagrama no PDF original que "
                "ainda não foi extraída. Consulte a prova em `data/exams/raw/`."
            )


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
