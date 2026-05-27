"""Agente validador de questões.

Dois modos:
  - structural: validação local (formato, completude, duplicatas). Sempre roda.
  - semantic: usa Anthropic API para verificar correção do gabarito e gerar
    explicações por alternativa. Requer ANTHROPIC_API_KEY no .env.

Uso (CLI):
  python -m src.agents.validator --all                # valida tudo
  python -m src.agents.validator --id oficial_2026-1_q01
  python -m src.agents.validator --pending            # só não-validadas
  python -m src.agents.validator --structural-only    # sem chamadas de API
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.data.load import load_bank, save_bank
from src.data.schema import (
    Alternativa,
    Origem,
    Question,
    QuestionBank,
    ValidacaoResult,
)

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
MODEL_DEFAULT = "claude-opus-4-7"

# ---------- Validação estrutural (sem API) ----------


def validate_structural(q: Question) -> list[str]:
    """Retorna lista de flags. Lista vazia = passou."""
    flags: list[str] = []
    if len(q.enunciado.strip()) < 20:
        flags.append("enunciado_muito_curto")
    chaves = [a.chave for a in q.alternativas]
    if len(set(chaves)) != len(chaves):
        flags.append("alternativas_duplicadas")
    if q.gabarito not in chaves:
        flags.append("gabarito_fora_das_alternativas")
    for a in q.alternativas:
        if len(a.texto.strip()) < 1:
            flags.append(f"alternativa_{a.chave}_vazia")
    # Heurística: enunciado quebrado quando termina sem pontuação e sem alternativas
    if not re.search(r"[.\?:!]\s*$", q.enunciado.strip()):
        flags.append("enunciado_sem_pontuacao_final")
    return flags


# ---------- Validação semântica (com API) ----------

VALIDATOR_SYSTEM_PROMPT = """Você é um professor de Ciência da Computação especialista no conteúdo da prova de seleção do Mestrado em Informática da UFES (PPGI). O conteúdo programático cobre:
1. Raciocínio Lógico (lógica proposicional, quantificadores, equivalência, argumentação)
2. Programação de Computadores (especialmente C: ponteiros, structs, escopo, stack/heap, trace de execução)
3. Linguagens e Paradigmas de Programação (imperativo, funcional, lógico, OO, herança, polimorfismo, SOLID)
4. Estruturas de Dados (listas, pilhas, filas, árvores, hash, grafos, BFS/DFS, ordenação, complexidade)

Sua tarefa: AVALIAR uma questão de múltipla escolha. Você DEVE:
1. Resolver a questão do zero, com raciocínio cuidadoso e passo-a-passo.
2. Comparar sua resposta com o gabarito fornecido.
3. Para CADA alternativa (a, b, c, d, e), escrever explicação curta (1-3 frases) sobre por que está certa OU errada.
4. Classificar o eixo principal (raciocinio_logico, programacao, paradigmas, estruturas_dados) e listar subtópicos relevantes.
5. Estimar dificuldade (facil/medio/dificil).
6. Atribuir confiança 0.0-1.0 na qualidade da questão e do gabarito.

Você DEVE responder em JSON estrito, sem texto fora do bloco JSON. Se discordar do gabarito, defina `gabarito_correto_segundo_voce` para a chave que considera certa e justifique em `raciocinio`.

Formato OBRIGATÓRIO:
{
  "raciocinio": "passos para resolver",
  "gabarito_correto_segundo_voce": "a|b|c|d|e",
  "concorda_com_gabarito": true,
  "explicacoes": {"a": "...", "b": "...", "c": "...", "d": "...", "e": "..."},
  "eixo": "raciocinio_logico|programacao|paradigmas|estruturas_dados",
  "subtopicos": ["..."],
  "dificuldade": "facil|medio|dificil",
  "confianca": 0.0,
  "flags": ["..."]
}"""


def _build_user_prompt(q: Question) -> str:
    linhas = [
        f"Questão: {q.enunciado}",
        "",
        "Alternativas:",
    ]
    for a in q.alternativas:
        linhas.append(f"({a.chave}) {a.texto}")
    linhas.extend(
        [
            "",
            f"Gabarito oficial declarado: {q.gabarito}",
            "",
            "Avalie estritamente no formato JSON especificado.",
        ]
    )
    return "\n".join(linhas)


def _extract_json(text: str) -> dict:
    """Extrai bloco JSON da resposta do modelo, tolerante a fences markdown."""
    # remove code fences se presentes
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    # senão pega entre o primeiro { e o último }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON não encontrado na resposta: {text[:200]}")
    return json.loads(text[start : end + 1])


def validate_semantic(q: Question, model: str = MODEL_DEFAULT) -> ValidacaoResult:
    """Roda validação semântica via Anthropic. Retorna ValidacaoResult."""
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError("anthropic SDK não instalado. pip install anthropic") from e

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY não configurada. Veja .env.example")

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        system=VALIDATOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(q)}],
    )
    text = "".join(block.text for block in resp.content if hasattr(block, "text"))
    data = _extract_json(text)

    flags: list[str] = list(data.get("flags", []))
    concorda = bool(data.get("concorda_com_gabarito", False))
    gabarito_modelo = data.get("gabarito_correto_segundo_voce", q.gabarito)
    confianca = float(data.get("confianca", 0.0))

    if not concorda:
        flags.append(f"discorda_gabarito_oficial:modelo_diz_{gabarito_modelo}")
        # reduz confiança se discordar e não for oficial
        if q.origem != Origem.oficial:
            confianca = min(confianca, 0.4)

    # Preenche explicações
    expl = data.get("explicacoes", {})
    novos_alts: list[Alternativa] = []
    for a in q.alternativas:
        e = expl.get(a.chave, a.explicacao)
        novos_alts.append(Alternativa(chave=a.chave, texto=a.texto, explicacao=e))
    q.alternativas = novos_alts

    # Aplica metadados retornados (sem sobrescrever se já tem)
    if data.get("eixo") in {"raciocinio_logico", "programacao", "paradigmas", "estruturas_dados"}:
        q.eixo = data["eixo"]  # type: ignore[assignment]
    subt = data.get("subtopicos") or []
    if subt and not q.subtopicos:
        q.subtopicos = subt
    dif = data.get("dificuldade")
    if dif in {"facil", "medio", "dificil"}:
        from src.data.schema import Dificuldade
        q.dificuldade = Dificuldade(dif)

    return ValidacaoResult(
        validado=True,
        confianca=confianca,
        raciocinio=data.get("raciocinio", ""),
        flags=flags,
        modelo=model,
        data=datetime.now(timezone.utc).isoformat(),
    )


# ---------- CLI ----------


def cli() -> None:
    parser = argparse.ArgumentParser(description="Agente validador de questões")
    parser.add_argument("--id", help="Validar questão específica por id")
    parser.add_argument("--all", action="store_true", help="Validar todas")
    parser.add_argument("--pending", action="store_true", help="Validar só as ainda não validadas")
    parser.add_argument("--structural-only", action="store_true", help="Sem chamada de API")
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--limit", type=int, default=None, help="Máximo de questões a validar")
    args = parser.parse_args()

    bank = load_bank()
    targets: list[Question] = []
    if args.id:
        targets = [q for q in bank.questions if q.id == args.id]
    elif args.pending:
        targets = [q for q in bank.questions if not q.validacao.validado]
    elif args.all:
        targets = list(bank.questions)
    else:
        parser.error("Use --id, --all, ou --pending")

    if args.limit:
        targets = targets[: args.limit]

    print(f"Validando {len(targets)} questões...")
    for i, q in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {q.id}")
        structural_flags = validate_structural(q)
        if structural_flags:
            print(f"  flags estruturais: {structural_flags}")
        if args.structural_only:
            q.validacao = ValidacaoResult(
                validado=True,
                confianca=0.5 if not structural_flags else 0.2,
                raciocinio="apenas validação estrutural",
                flags=structural_flags,
                modelo="structural",
                data=datetime.now(timezone.utc).isoformat(),
            )
        else:
            try:
                result = validate_semantic(q, model=args.model)
                result.flags = structural_flags + result.flags
                q.validacao = result
                print(f"  confiança: {result.confianca:.2f}; flags: {result.flags}")
            except Exception as e:
                print(f"  ERRO semântico: {e}")
                q.validacao = ValidacaoResult(
                    validado=False,
                    confianca=0.0,
                    raciocinio=f"erro: {e}",
                    flags=structural_flags + ["erro_validacao_semantica"],
                    modelo="error",
                    data=datetime.now(timezone.utc).isoformat(),
                )

        # salva incrementalmente
        save_bank(bank)

    print("Concluído.")


if __name__ == "__main__":
    cli()
