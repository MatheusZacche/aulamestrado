# Aulamestrado

App estilo cursinho para a prova de seleção do **Mestrado em Informática (PPGI) da UFES**.

Banco de questões com as provas oficiais publicamente disponíveis + questões geradas e validadas por agente, com explicações por alternativa.

## Status

- Provas oficiais incorporadas: **2026/1, 2025/2, 2025/1** (únicas disponibilizadas publicamente pelo PPGI/UFES na data deste repositório).
- Banco de questões validadas: em construção.
- Modos: Estudo, Simulado, Estatísticas, Salvas, Notas.

## Conteúdo programático oficial (Edital PPGI 03/2026)

1. Raciocínio Lógico
2. Programação de Computadores
3. Linguagens e Paradigmas de Programação
4. Estruturas de Dados

Formato da prova: 20 questões objetivas, 5 alternativas, 2h, mínimo 60% (eliminatório).

## Rodando localmente

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Abre em http://localhost:8501. Funciona no celular acessando o IP local.

## Estrutura

```
.
├── app.py                          # Entry Streamlit (home)
├── pages/                          # Páginas multi-page
│   ├── 1_📚_Estudar.py
│   ├── 2_📝_Simulado.py
│   ├── 3_📊_Estatísticas.py
│   ├── 4_🔖_Salvas.py
│   └── 5_ℹ️_Sobre.py
├── data/
│   ├── exams/raw/                  # PDFs originais das provas
│   ├── exams/text/                 # Texto extraído (gitignored)
│   ├── questions.json              # Banco de questões consolidado
│   └── topics.json                 # Taxonomia de tópicos/subtópicos
├── src/
│   ├── data/
│   │   ├── extract_pdfs.py         # PDF → texto
│   │   ├── parse_exam.py           # Texto da prova → questões JSON
│   │   ├── schema.py               # Modelos Pydantic
│   │   └── load.py                 # Carregamento do banco
│   ├── agents/
│   │   └── validator.py            # Agente validador de questões
│   └── ui/
│       └── components.py           # Componentes Streamlit
├── tests/
├── requirements.txt
└── README.md
```

## Pipeline de questões

1. **Provas oficiais** → `extract_pdfs.py` → `parse_exam.py` → `questions.json` com `origem=oficial_YYYY-S`
2. **Geradas** → batch generator → `validator.py` → marca `confianca` 0-1 → se ≥ 0.8 entra no banco com `origem=gerada_validada`
3. **Anuladas oficialmente** → flag `anulada=True` (questão é mostrada mas não conta no simulado)

## Agente validador

Para cada questão, verifica:
1. **Integridade**: enunciado completo, 5 alternativas distintas, gabarito mapeia para alternativa existente
2. **Correção**: raciocínio passo a passo para confirmar/refutar gabarito
3. **Explicações**: por alternativa, por que está certa ou errada
4. **Dificuldade**: estimativa fácil/médio/difícil
5. **Confiança final**: 0-1

Implementado em `src/agents/validator.py`. Requer `ANTHROPIC_API_KEY` no `.env`.

## Fontes oficiais

- [Editais e provas PPGI/UFES](https://informatica.ufes.br/pt-br/processos-seletivos-editais-passados)
- [Edital 03/2026 (2026/2)](https://informatica.ufes.br/sites/informatica.ufes.br/files/field/anexo/edital-mestrado-ppgi-2026-2.pdf)

## Licença

Conteúdo das provas oficiais é de propriedade do PPGI/UFES. Este projeto é educacional pessoal e não tem afiliação com a UFES.
