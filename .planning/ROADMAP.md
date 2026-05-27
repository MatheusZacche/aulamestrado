# Roadmap — Aulamestrado

## Fase 0 — Bootstrap (✅ concluída)

- Clonar repo público vazio
- Estrutura de pastas + .gitignore + requirements + README
- PROJECT.md, ROADMAP.md
- Schema canônico de questão (Pydantic)

## Fase 1 — Provas oficiais como base (✅ concluída)

- Identificar provas disponíveis (resultado: 3 — 2026/1, 2025/2, 2025/1)
- Baixar PDFs (provas + gabaritos + edital 03/2026)
- Extrator PDF → texto (pdfplumber)
- Parser texto → JSON canônico (60 questões)
- Marcação de questões anuladas

## Fase 2 — Agente validador (✅ concluída)

- Validação estrutural local (sem API)
- Validação semântica via Anthropic (com API key opcional)
- Salvamento incremental no banco

## Fase 3 — App Streamlit (✅ concluída)

- Home + métricas
- Modo Estudo com filtros, feedback, bookmark, notas, auto-avaliação
- Modo Simulado com cronômetro 2h e revisão pós-prova
- Estatísticas por eixo, subtópico, calibração de confiança
- Salvas (bookmarked + erradas anteriormente)

## Fase 4 — Banco gerado (em progresso)

- 12 sementes manuais validadas (todos os 4 eixos cobertos)
- Gerador de questões via Anthropic (gerar_lote, plano balanceado)
- **Próximo**: usuário roda `python -m src.agents.generator --balanced --total 150`
  e em seguida `python -m src.agents.validator --pending` para popular até 150+ validadas.

## Fase 5 — Deploy (em progresso)

- Push para GitHub: MatheusZacche/aulamestrado
- Smoke test local
- **Próximo**: configurar Streamlit Cloud (gratuito, conecta direto ao repo público)

## Fase 6 — Ampliações futuras (não priorizadas)

- Repetição espaçada com agendamento de revisão
- Modo "explicações em vídeo" (links externos)
- Suporte a anexos/imagens em questões (matrizes, diagramas)
- Exportação de relatório PDF de desempenho
- Achar provas pré-2025 (contato com a comissão PPGI)
