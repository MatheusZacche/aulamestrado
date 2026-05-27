"""Testes do schema canônico de questão."""
from __future__ import annotations

import pytest

from src.data.schema import Alternativa, Origem, Question


def _alts():
    return [
        Alternativa(chave="a", texto="primeira"),
        Alternativa(chave="b", texto="segunda"),
        Alternativa(chave="c", texto="terceira"),
        Alternativa(chave="d", texto="quarta"),
        Alternativa(chave="e", texto="quinta"),
    ]


def test_question_valida():
    q = Question(
        id="t1",
        origem=Origem.oficial,
        eixo="raciocinio_logico",
        enunciado="Enunciado de teste com pelo menos vinte caracteres.",
        alternativas=_alts(),
        gabarito="a",
    )
    assert q.gabarito == "a"
    assert len(q.alternativas) == 5


def test_alternativas_duplicadas_rejeitadas():
    alts = _alts()
    alts[1].chave = "a"  # type: ignore[assignment]
    with pytest.raises(ValueError):
        Question(
            id="t2",
            origem=Origem.oficial,
            eixo="programacao",
            enunciado="Enunciado de teste com pelo menos vinte caracteres.",
            alternativas=alts,
            gabarito="a",
        )


def test_serializa_roundtrip():
    q = Question(
        id="t3",
        origem=Origem.oficial,
        eixo="estruturas_dados",
        enunciado="Enunciado de teste com pelo menos vinte caracteres.",
        alternativas=_alts(),
        gabarito="c",
    )
    raw = q.model_dump_json()
    q2 = Question.model_validate_json(raw)
    assert q2.id == q.id
    assert q2.gabarito == q.gabarito
