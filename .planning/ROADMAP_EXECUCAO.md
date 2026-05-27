# Roadmap de Execução — Aulamestrado

**Modo:** sem API (zero custo). Toda explicação e geração escritas manualmente pelo assistente em batches, committed incrementalmente.

**Meta final:** 150+ questões com explicação por alternativa, deploy no Streamlit Cloud, app pronto para uso pelo PC e celular.

---

## Fase A — Explicações nas 60 questões oficiais (CRÍTICO)

Cada questão oficial precisa ganhar:
- Explicação por alternativa (5 explicações)
- `eixo` refinado (hoje todas estão como `raciocinio_logico` placeholder)
- `subtopicos` preenchidos
- `dificuldade` ajustada
- `validacao` com confiança 0.9 e modelo "curadoria_manual"

**Implementação:** arquivo `src/data/seed_oficiais_explicacoes.py` aplica via `add_or_update`. Idempotente — pode rodar várias vezes.

- [ ] **A1** Prova 2026/1 (20 questões) — mais recente, melhor referência
- [ ] **A2** Prova 2025/2 (19 questões + 1 anulada Q5)
- [ ] **A3** Prova 2025/1 (20 questões)

Após cada batch: `python -m src.data.seed_oficiais_explicacoes`, `pytest`, commit.

## Fase B — Polimento de UI e parser (alta prioridade)

- [ ] **B1** Renderizar código C em bloco monospace (detecção: presença de `;`, `printf`, `int main`, etc) — afeta 2026/1 Q10/15/17/18 e equivalentes
- [ ] **B2** Schema gain `tem_imagem: bool` + UI exibe aviso "Esta questão original tinha figura — descrita no enunciado" — afeta 2026/1 Q19 (árvore B)
- [ ] **B3** Auto-refresh do cronômetro do simulado (a cada 30s)
- [ ] **B4** Limpeza dos enunciados oficiais (caracteres `~`, `→`, ligaduras quebradas do PDF)

## Fase C — Banco gerado manual (78 questões → total 150)

Distribuição alvo dos 78: ~20 por eixo (78/4 ≈ 19.5). Já temos 12 geradas (3 por eixo). Alvo final ~22 geradas por eixo.

- [ ] **C1** Lote raciocínio_lógico (+15 = 18 total)
- [ ] **C2** Lote programação (+15 = 18 total)
- [ ] **C3** Lote paradigmas (+15 = 18 total)
- [ ] **C4** Lote estruturas_dados (+15 = 18 total)
- [ ] **C5** Buffer (+18 distribuído pelos eixos mais fracos do banco) — confirma 150 total

Cada questão segue o estilo PPGI: 5 alternativas, "Nenhuma das anteriores" em ~25%, mistura conceito+trace, dificuldade média a alta.

## Fase D — Deploy Streamlit Cloud

- [ ] **D1** Smoke test local final (todas as páginas, simulado completo, estatísticas com dados)
- [ ] **D2** Criar conta/login share.streamlit.io (instruções pro usuário, não posso fazer)
- [ ] **D3** Apontar app pra `MatheusZacche/aulamestrado` branch `main`, entry `app.py`
- [ ] **D4** Verificar URL pública no celular
- [ ] **D5** README seção "Acesso público" com URL

## Fase E — Nice-to-have (opcional, pós-deploy)

- [ ] Modo escuro/light com tema custom
- [ ] Aviso visual quando faltam 30min no simulado (igual prova real)
- [ ] Export PDF do relatório de desempenho
- [ ] Repetição espaçada (questão errada volta em 1d, 3d, 7d)
- [ ] Anotação de fórmulas em LaTeX nas explicações

---

## Ordem de execução (sequencial, com commits)

```
A1  →  commit  →  A2  →  commit  →  A3  →  commit
            ↓
    B1+B2+B4 (UI polish + parser cleanup)  →  commit
            ↓
        B3 (timer)  →  commit
            ↓
    C1 → commit → C2 → commit → C3 → commit → C4 → commit → C5 → commit
            ↓
        D1 (smoke test final)  →  commit
            ↓
    D2/D3 (passo manual do usuário no Streamlit Cloud)
            ↓
        D4/D5 (validar + documentar URL)  →  commit
```

## Estimativa de esforço (minha mão)

- Fase A: ~3 turns de chat (1 prova por turn)
- Fase B: 1 turn
- Fase C: ~4 turns (1 lote de 15 por turn)
- Fase D: 1 turn (D1, D5) + manual user (D2, D3, D4)

Total: ~9 turns/iterações para chegar em "completo".

## Política de qualidade

- Cada questão escrita ou explicada vai com `confianca: 0.9` e `modelo: curadoria_manual`
- Se eu tiver dúvida no gabarito oficial, marco flag `requer_revisao_humana` na questão (você decide)
- Nada de "explicação genérica" — cada alternativa ganha por que está certa OU errada, com referência ao conceito específico
- Commits atômicos: 1 fase = 1 commit (exceto C que vira 5)
