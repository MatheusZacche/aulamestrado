# Aulamestrado — Projeto GSD

## Visão

App pessoal de preparação para a prova de seleção do **Mestrado em Informática (PPGI) da UFES**, estilo cursinho: banco de questões com explicações por alternativa, modo Estudo e modo Simulado, estatísticas de progresso, validação de qualidade por agente.

## Por que existe

- O usuário está se preparando para a entrada 2026/2 do PPGI/UFES.
- Provas oficiais são poucas (apenas 3 disponíveis publicamente: 2026/1, 2025/2, 2025/1).
- Preparação eficiente exige um corpus maior, validado, com explicações didáticas.
- Acesso pelo celular e pelo computador (Streamlit).

## Stakeholders

- Usuário único (Matheus) — autor e estudante.
- Eventual público futuro se o repo virar comunitário.

## Princípios

1. **Verdade sobre conveniência**: nunca passar questão sem validação. Cada questão tem `origem` clara.
2. **Local-first**: progresso fica em arquivo local, sem servidor, sem login.
3. **Sem alucinação**: gabarito + explicação SEMPRE conferidos pelo agente validador.
4. **Reproduz o real**: o modo Simulado replica o formato oficial (20q, 2h, 60% corte).
5. **Iteração rápida**: localhost primeiro, Streamlit Cloud depois.

## Stack

- Python 3.12+
- Streamlit (multipage)
- pdfplumber (PDF → texto)
- Pydantic v2 (schema)
- Anthropic SDK (validador + gerador)
- Persistência: JSON (não há motivo para SQLite ainda)

## Tópicos cobertos (Edital 03/2026 PPGI)

1. Raciocínio Lógico — Mortari
2. Programação de Computadores — Celes/Cerqueira/Rangel + Cormen
3. Linguagens e Paradigmas — Tucker, Noonan
4. Estruturas de Dados — Celes/Cerqueira/Rangel + Cormen

## Não-objetivos (escopo cortado)

- Gamificação / ranking social
- IA tutor conversacional (chat de tira-dúvidas)
- Backend com login multiusuário
- Suporte a outras universidades (foco PPGI/UFES)
- Geração automática de imagens/diagramas para questões
