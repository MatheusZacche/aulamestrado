"""Gerador de questões no estilo PPGI/UFES.

Pipeline:
1. Para cada subtópico, pede ao modelo para criar N questões.
2. Cada questão gerada é salva em status `gerada_rascunho`.
3. Em seguida o validador (src.agents.validator) é chamado para validar.
4. Só questões com confiança ≥ 0.8 ficam visíveis no app.

Uso:
  python -m src.agents.generator --batch 30                  # 30 questões aleatórias
  python -m src.agents.generator --eixo programacao --n 10   # 10 de programação
  python -m src.agents.generator --balanced --total 150      # 150 distribuídas
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.data.load import add_or_update, load_bank, load_topics, save_bank
from src.data.schema import (
    Alternativa,
    Dificuldade,
    Origem,
    Question,
    ValidacaoResult,
)

load_dotenv()
MODEL_DEFAULT = "claude-opus-4-7"

GENERATOR_SYSTEM = """Você é um professor de Ciência da Computação criando questões
no estilo da prova de seleção do Mestrado em Informática da UFES (PPGI).

Características do estilo PPGI:
- 5 alternativas (a, b, c, d, e), apenas UMA correta
- Frequentemente usa "Nenhuma das alternativas anteriores" como (e)
- Mistura conceitos teóricos com pequenos traces de código em C
- Costuma usar formato "Considere as afirmativas I, II, III. Está correto:"
- Linguagem técnica em português acadêmico, sem coloquialismos
- Dificuldade média a alta — exige domínio dos conceitos, não decoreba

Você DEVE responder em JSON estrito, no formato:
{
  "enunciado": "...",
  "alternativas": [
    {"chave": "a", "texto": "...", "explicacao": "Por que está certa/errada"},
    {"chave": "b", "texto": "...", "explicacao": "..."},
    {"chave": "c", "texto": "...", "explicacao": "..."},
    {"chave": "d", "texto": "...", "explicacao": "..."},
    {"chave": "e", "texto": "...", "explicacao": "..."}
  ],
  "gabarito": "a|b|c|d|e",
  "dificuldade": "facil|medio|dificil",
  "subtopicos": ["..."]
}"""


def _extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON não encontrado: {text[:200]}")
    return json.loads(text[start : end + 1])


def gerar_uma(eixo: str, subtopico: str, model: str = MODEL_DEFAULT) -> Question:
    from anthropic import Anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY não configurada")

    topics = load_topics()
    biblio = topics["eixos"][eixo]["bibliografia"]
    biblio_str = "; ".join(biblio)

    client = Anthropic(api_key=api_key)
    user = (
        f"Crie UMA questão de múltipla escolha sobre o eixo '{eixo}', "
        f"subtópico '{subtopico}'. Bibliografia oficial: {biblio_str}. "
        "Inclua explicação por alternativa. Responda APENAS o JSON especificado."
    )
    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        system=GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if hasattr(b, "text"))
    data = _extract_json(text)

    bank = load_bank()
    existing_n = sum(1 for q in bank.questions if q.id.startswith("gerada_"))
    new_id = f"gerada_{existing_n + 1:04d}"

    alts = [
        Alternativa(
            chave=a["chave"],
            texto=a["texto"],
            explicacao=a.get("explicacao", ""),
        )
        for a in data["alternativas"]
    ]
    return Question(
        id=new_id,
        origem=Origem.gerada_rascunho,
        eixo=eixo,  # type: ignore[arg-type]
        subtopicos=data.get("subtopicos") or [subtopico],
        ano=None,
        numero_na_prova=None,
        enunciado=data["enunciado"],
        alternativas=alts,
        gabarito=data["gabarito"],  # type: ignore[arg-type]
        dificuldade=Dificuldade(data.get("dificuldade", "medio")),
        validacao=ValidacaoResult(
            validado=False,
            confianca=0.0,
            raciocinio="recém-gerada; aguarda validação",
            flags=[],
            modelo=model,
            data=datetime.now(timezone.utc).isoformat(),
        ),
    )


def gerar_lote(plano: list[tuple[str, str]], model: str = MODEL_DEFAULT) -> int:
    """plano = [(eixo, subtopico), ...]. Retorna número de questões adicionadas."""
    bank = load_bank()
    adicionadas = 0
    for i, (eixo, sub) in enumerate(plano, 1):
        print(f"[{i}/{len(plano)}] Gerando {eixo}/{sub}...")
        try:
            q = gerar_uma(eixo, sub, model=model)
            bank = add_or_update(bank, q)
            adicionadas += 1
            save_bank(bank)  # incremental
        except Exception as e:
            print(f"  ERRO: {e}")
    return adicionadas


def plano_balanceado(total: int) -> list[tuple[str, str]]:
    topics = load_topics()
    pares: list[tuple[str, str]] = []
    for eixo_key, eixo in topics["eixos"].items():
        for sub in eixo["subtopicos"]:
            pares.append((eixo_key, sub))
    random.shuffle(pares)
    # Repete a lista até atingir o total
    out: list[tuple[str, str]] = []
    while len(out) < total:
        out.extend(pares)
    return out[:total]


def cli() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--eixo", default=None)
    p.add_argument("--subtopico", default=None)
    p.add_argument("--balanced", action="store_true")
    p.add_argument("--total", type=int, default=20)
    p.add_argument("--batch", type=int, default=None,
                   help="N questões aleatoriamente distribuídas")
    p.add_argument("--model", default=MODEL_DEFAULT)
    args = p.parse_args()

    if args.balanced:
        plano = plano_balanceado(args.total)
    elif args.batch:
        plano = plano_balanceado(args.batch)
    elif args.eixo and args.subtopico:
        plano = [(args.eixo, args.subtopico)] * args.n
    elif args.eixo:
        topics = load_topics()
        subs = topics["eixos"][args.eixo]["subtopicos"]
        plano = [(args.eixo, random.choice(subs)) for _ in range(args.n)]
    else:
        p.error("Use --balanced --total N, ou --batch N, ou --eixo X [--subtopico Y] --n K")

    print(f"Plano: {len(plano)} questões a gerar")
    n = gerar_lote(plano, model=args.model)
    print(f"\nGeradas {n} questões. Agora rode o validador:")
    print(f"  python -m src.agents.validator --pending")


if __name__ == "__main__":
    cli()
