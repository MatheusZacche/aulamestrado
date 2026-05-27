"""Sobre o projeto."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Sobre — Aulamestrado", page_icon="ℹ️", layout="wide")
st.title("ℹ️ Sobre")

st.markdown(
    """
**Aulamestrado** é um app pessoal de preparação para a prova de seleção do
**Mestrado em Informática (PPGI) da UFES**.

## Como o banco é construído

1. **Provas oficiais**: PDFs baixados do site do PPGI/UFES são extraídos para texto e parseados em questões canônicas. As 3 provas disponíveis publicamente são 2026/1, 2025/2 e 2025/1.

2. **Questões geradas**: questões adicionais geradas por LLM passam por um **agente validador** que:
   - Resolve a questão do zero
   - Compara com o gabarito
   - Atribui confiança 0–1
   - Gera explicação por alternativa
   - Marca dificuldade e subtópicos

3. **Critério de inclusão**: só entram no banco questões com confiança ≥ 0.8. As demais ficam em revisão.

## O agente validador

Implementação em `src/agents/validator.py`. Dois modos:

- **Estrutural** (sem API): verifica integridade, alternativas únicas, gabarito coerente.
- **Semântico** (com Anthropic API): verifica correção do gabarito, gera explicações.

Para rodar:
```bash
python -m src.agents.validator --pending          # só não validadas
python -m src.agents.validator --all              # tudo
python -m src.agents.validator --id <question_id> # uma específica
```

## Conteúdo programático (Edital 03/2026)

1. Raciocínio Lógico — Mortari
2. Programação de Computadores — Celes, Cerqueira, Rangel Netto + Cormen
3. Linguagens e Paradigmas — Tucker, Noonan
4. Estruturas de Dados — Celes, Cerqueira, Rangel Netto + Cormen

## Formato oficial

- 20 questões objetivas, 5 alternativas, 1 correta
- 40 pontos totais, mínimo **60% (eliminatório)**
- 2 horas de duração

## Privacidade

Progresso e anotações ficam **localmente** em `data/user_progress.json` (gitignored). Nada é enviado para servidores.

## Fontes oficiais

- [Processos seletivos PPGI/UFES](https://informatica.ufes.br/pt-br/processos-seletivos)
- [Edital 03/2026 (2026/2)](https://informatica.ufes.br/sites/informatica.ufes.br/files/field/anexo/edital-mestrado-ppgi-2026-2.pdf)
"""
)
