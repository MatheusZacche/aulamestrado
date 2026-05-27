# Aulamestrado

App estilo cursinho para a prova de seleção do **Mestrado em Informática (PPGI) da UFES**.

Banco com **150 questões validadas** (60 oficiais + 90 geradas), todas com explicação por alternativa. Modos: Estudo, Simulado, Estatísticas, Salvas.

## Status

| Componente | Estado |
|---|---|
| Provas oficiais (PDFs + parser) | ✅ 3 provas: 2026/1, 2025/2, 2025/1 |
| Banco com explicações por alternativa | ✅ 150/150 questões |
| Validação (confiança ≥ 0.8) | ✅ 150/150 |
| Modo Estudo | ✅ Filtros, feedback, bookmark, notas, autoavaliação |
| Modo Simulado | ✅ Cronometrado 2h, distribuído 4 eixos, corte 60% |
| Estatísticas | ✅ Por eixo/subtópico, calibração, histórico |
| Auto-refresh cronômetro | ✅ Via streamlit-autorefresh |
| Renderização código C monospace | ✅ Detecção heurística |
| Flag imagens não extraídas | ✅ 2 questões marcadas (avisos) |
| Deploy Streamlit Cloud | ⏳ Aguardando configuração manual |

## Conteúdo programático oficial (Edital PPGI 03/2026)

1. **Raciocínio Lógico** — proposições, quantificadores, equivalência, argumentação (Mortari)
2. **Programação de Computadores** — C: ponteiros, structs, memória, escopo, trace (Celes/Cerqueira/Rangel + Cormen)
3. **Linguagens e Paradigmas** — imperativo, funcional, lógico, OO, SOLID, tipagem (Tucker & Noonan)
4. **Estruturas de Dados** — listas, pilhas, filas, árvores, hash, grafos, ordenação, complexidade (Celes/Cerqueira/Rangel + Cormen)

**Formato da prova:** 20 questões objetivas, 5 alternativas, 2h, mínimo 60% (eliminatório).

**Distribuição atual do banco:**
- Estruturas de dados: 41
- Paradigmas: 39
- Programação: 35
- Raciocínio lógico: 35

## Rodando localmente

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Roda
streamlit run app.py
```

Abre em http://localhost:8501. No celular pela mesma Wi-Fi: usa o `Network URL` que o Streamlit imprime.

## Deploy no Streamlit Cloud (acesso público pelo celular)

Pré-requisitos: repositório público no GitHub (já está) e conta no Streamlit Cloud (grátis).

1. Acesse https://share.streamlit.io
2. Login com sua conta GitHub
3. **New app** → seleciona repo `MatheusZacche/aulamestrado`
4. Branch: `main`
5. Main file path: `app.py`
6. Python version: 3.11 (compatível, embora local rode 3.14)
7. Deploy

Em ~2 minutos fica online em `https://<seu-app>.streamlit.app`. Adiciona aos favoritos do celular.

**Observação importante:** progresso e anotações são salvos LOCALMENTE no servidor do Streamlit Cloud, sem garantia de persistência (containers reiniciam). Para uso pessoal de estudo essa é uma limitação aceitável; para histórico permanente, rodar localmente.

## Estrutura

```
.
├── app.py                          # Home
├── pages/                          # Streamlit multipage
│   ├── 1_Estudar.py
│   ├── 2_Simulado.py
│   ├── 3_Estatisticas.py
│   ├── 4_Salvas.py
│   └── 5_Sobre.py
├── data/
│   ├── exams/raw/                  # 3 PDFs oficiais + editais
│   ├── exams/text/                 # Texto extraído (gitignored)
│   ├── questions.json              # 150 questões consolidadas
│   └── topics.json                 # Taxonomia
├── src/
│   ├── data/
│   │   ├── schema.py               # Modelos Pydantic
│   │   ├── load.py                 # Persistência
│   │   ├── progress.py             # Progresso local
│   │   ├── extract_pdfs.py         # PDF → texto
│   │   ├── parse_exam.py           # Texto → JSON
│   │   ├── seed_geradas.py         # 12 sementes iniciais
│   │   ├── seed_oficiais_explicacoes.py  # Explicações para 60 oficiais
│   │   └── seed_lotes.py           # 78 geradas em lotes (C1-C5)
│   ├── agents/
│   │   ├── validator.py            # Agente validador (estrutural + semântico)
│   │   └── generator.py            # Gerador de questões via API
│   └── ui/
│       └── components.py           # Componentes Streamlit
├── tests/                          # pytest (6 testes)
├── .planning/
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   └── ROADMAP_EXECUCAO.md         # Roadmap manual sem API
└── requirements.txt
```

## Pipeline de questões

1. **Oficiais**: `extract_pdfs.py` → `parse_exam.py` → `seed_oficiais_explicacoes.py` aplica explicações
2. **Geradas manuais**: `seed_geradas.py` (12) + `seed_lotes.py` (78) — todas com explicação por alternativa
3. **Geradas via API** (opcional, para expandir): `agents/generator.py` → `agents/validator.py`

Todas as questões têm campo `origem` (`oficial`, `gerada_validada`), `validacao.confianca` (0-1), e flag `tem_imagem` para questões cujas figuras não foram extraídas.

## Agente validador

Implementação em `src/agents/validator.py`. Dois modos:

```bash
# Estrutural (sem API): verifica formato, alternativas únicas, gabarito coerente
python -m src.agents.validator --all --structural-only

# Semântico (com Anthropic): verifica gabarito, gera explicações por alternativa
python -m src.agents.validator --all   # requer ANTHROPIC_API_KEY no .env
```

## Persistência de progresso

Dois backends suportados, escolhidos automaticamente:

| Cenário | Backend ativo |
|---|---|
| Sem variáveis configuradas | **JSON local** em `data/user_progress.json` (gitignored) |
| `SUPABASE_URL` + `SUPABASE_ANON_KEY` configuradas | **Supabase Postgres** (sincroniza celular ↔ PC) |

### Setup do Supabase (passo a passo)

1. Crie conta grátis em https://supabase.com e um **novo projeto** (qualquer região, senha qualquer).
2. No painel do projeto: **SQL Editor** → cole o conteúdo de [`supabase/schema.sql`](supabase/schema.sql) → **Run**. Isso cria as 4 tabelas.
3. No painel: **Settings** → **API** → copie:
   - **Project URL** → vira `SUPABASE_URL`
   - **anon public** key → vira `SUPABASE_ANON_KEY`
4. **Localmente**: copie `.env.example` → `.env` e preencha. Ou copie `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`.
5. **No Streamlit Cloud**: vá no painel do app → **Settings** → **Secrets** → cole no formato:
   ```toml
   SUPABASE_URL = "https://xxxxx.supabase.co"
   SUPABASE_ANON_KEY = "eyJhbGc..."
   ```
   Salva. O app redeploya automaticamente.

A sidebar do app mostra qual backend está ativo (`☁️ Progresso na nuvem` ou `💾 Progresso local`).

**Por que isso é seguro sendo single-user:** a anon key não vai pro repo (gitignored localmente, em Secrets no Cloud). Sem RLS porque você é o único usuário com a chave. Se algum dia compartilhar o app, refaça com auth.

## Fontes oficiais

- [Processos seletivos PPGI/UFES](https://informatica.ufes.br/pt-br/processos-seletivos)
- [Edital 03/2026 (mestrado 2026/2)](https://informatica.ufes.br/sites/informatica.ufes.br/files/field/anexo/edital-mestrado-ppgi-2026-2.pdf)

## Licença

Conteúdo das provas oficiais é de propriedade do PPGI/UFES. Este projeto é uso educacional pessoal, sem afiliação com a UFES.
