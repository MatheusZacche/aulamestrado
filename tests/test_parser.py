"""Smoke tests do parser de provas."""
from __future__ import annotations

from pathlib import Path

from src.data.parse_exam import parse_alternativas, read_gabarito, split_questions

ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "data" / "exams" / "text"


def test_split_questions_minimal():
    raw = "Questão 1: Qual é a cor do céu?\na) Azul\nb) Verde\n\n" \
          "Questão 2: Quanto é 2+2?\na) 3\nb) 4\n"
    out = split_questions(raw)
    assert len(out) == 2
    assert out[0][0] == 1
    assert "azul" in out[0][1].lower()


def test_parse_alternativas_basico():
    bloco = "Qual a cor do céu?\na) Azul\nb) Verde\nc) Vermelho\nd) Amarelo\ne) Nenhuma das anteriores"
    enunciado, alts = parse_alternativas(bloco)
    assert "céu" in enunciado.lower()
    assert len(alts) == 5
    assert alts[0].chave == "a"
    assert "azul" in alts[0].texto.lower()


def test_gabarito_real_se_existir():
    """Se os PDFs já foram extraídos, o gabarito deve ter 20 entradas."""
    g = TEXT_DIR / "ppgi_2026-1_gabarito.txt"
    if not g.exists():
        return  # smoke condicional
    gab = read_gabarito(g)
    assert len(gab) == 20
    assert all(v in {"a", "b", "c", "d", "e", "anulada"} for v in gab.values())
