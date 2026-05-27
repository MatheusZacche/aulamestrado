"""Parser de provas PPGI UFES (texto extraído do PDF -> JSON canônico).

Estratégia:
  1. Lê o .txt extraído de uma prova oficial.
  2. Lê o .txt do gabarito correspondente.
  3. Quebra o texto da prova em questões pelo marcador "Questão N:".
  4. Para cada questão, separa enunciado das alternativas (a..e).
  5. Cruza com o gabarito para preencher o campo `gabarito`.
  6. Marca questões anuladas com `anulada=True`.

Limitações conhecidas:
  - Questões com código C ou matriz/grafo em layout complexo podem ficar com
    espaços/quebras estranhas. O agente validador deve flaggar isso.
  - Tags de subtópico são inicialmente vazias; preenchidas após validação.
"""
from __future__ import annotations

import re
from pathlib import Path

from .schema import Alternativa, Origem, Question

ROOT = Path(__file__).resolve().parents[2]
TEXT_DIR = ROOT / "data" / "exams" / "text"

QUESTAO_RE = re.compile(r"Quest[ãa]o\s+(\d{1,2})\s*:\s*", re.IGNORECASE)
ALT_RE = re.compile(r"^\s*([a-e])[\)\.\s]", re.IGNORECASE | re.MULTILINE)
GABARITO_RE = re.compile(r"^\s*(\d{1,2})\s+([a-eA-E]|Anulada)\s*$", re.MULTILINE)
PAGE_BREAK_RE = re.compile(r"=== PAGE \d+ ===")


def _clean(text: str) -> str:
    text = PAGE_BREAK_RE.sub("", text)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def read_gabarito(gabarito_txt: Path) -> dict[int, str]:
    raw = gabarito_txt.read_text(encoding="utf-8")
    out: dict[int, str] = {}
    for m in GABARITO_RE.finditer(raw):
        n = int(m.group(1))
        ans = m.group(2)
        out[n] = ans.lower() if ans.lower() != "anulada" else "anulada"
    return out


def split_questions(prova_text: str) -> list[tuple[int, str]]:
    """Retorna [(numero, bloco_de_texto), ...] ordenado por número."""
    body = _clean(prova_text)
    matches = list(QUESTAO_RE.finditer(body))
    out: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        n = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[start:end].strip()
        out.append((n, block))
    return out


def parse_alternativas(block: str) -> tuple[str, list[Alternativa]]:
    """Separa enunciado de alternativas usando a primeira ocorrência de 'a)' ou 'a.'."""
    # Procura por linha que começa com "a)" ou "a." marcando o início das alternativas.
    first_alt = None
    for m in ALT_RE.finditer(block):
        if m.group(1).lower() == "a":
            first_alt = m
            break
    if first_alt is None:
        return block.strip(), []

    enunciado = block[: first_alt.start()].strip()
    alts_raw = block[first_alt.start():]

    # Quebra alternativas: assume que cada alternativa começa numa linha própria com letra
    alts: list[Alternativa] = []
    positions: list[tuple[str, int]] = []
    for m in ALT_RE.finditer(alts_raw):
        positions.append((m.group(1).lower(), m.start()))

    for i, (key, pos) in enumerate(positions):
        end = positions[i + 1][1] if i + 1 < len(positions) else len(alts_raw)
        texto = alts_raw[pos:end]
        # Remove o "a)" inicial
        texto = re.sub(r"^\s*[a-e][\)\.\s]+", "", texto, count=1, flags=re.IGNORECASE).strip()
        if key in {a.chave for a in alts}:
            continue  # ignora repetição
        alts.append(Alternativa(chave=key, texto=texto))  # type: ignore[arg-type]

    return enunciado, alts


def parse_prova(prova_txt: Path, gabarito_txt: Path, ano_label: str) -> list[Question]:
    text = prova_txt.read_text(encoding="utf-8")
    gabarito = read_gabarito(gabarito_txt)
    questions: list[Question] = []
    for numero, bloco in split_questions(text):
        enunciado, alts = parse_alternativas(bloco)
        if not alts:
            # Não conseguiu extrair alternativas — pula com aviso
            print(f"  ! Q{numero}: alternativas não encontradas (revisar manualmente)")
            continue
        gab = gabarito.get(numero, "")
        anulada = gab == "anulada"
        # Para anuladas, marca gabarito como "a" provisoriamente (não conta no app)
        gabarito_final = "a" if anulada else gab
        if gabarito_final not in {"a", "b", "c", "d", "e"}:
            print(f"  ! Q{numero}: gabarito ausente, marcando para revisão")
            gabarito_final = "a"

        q = Question(
            id=f"oficial_{ano_label}_q{numero:02d}",
            origem=Origem.oficial,
            eixo="raciocinio_logico",  # placeholder; o validador refina
            subtopicos=[],
            ano=ano_label,
            numero_na_prova=numero,
            enunciado=enunciado,
            alternativas=alts,
            gabarito=gabarito_final,  # type: ignore[arg-type]
            anulada=anulada,
            motivo_anulacao="Anulada pela banca." if anulada else "",
        )
        questions.append(q)
    return questions


def parse_all() -> list[Question]:
    """Processa todas as provas em data/exams/text/*_prova.txt"""
    out: list[Question] = []
    pares: list[tuple[Path, Path, str]] = []
    for prova in sorted(TEXT_DIR.glob("ppgi_*_prova.txt")):
        # Espera nome ppgi_YYYY-S_prova.txt
        stem = prova.stem  # ppgi_2026-1_prova
        ano_label = stem.replace("ppgi_", "").replace("_prova", "")
        gabarito = TEXT_DIR / f"ppgi_{ano_label}_gabarito.txt"
        if not gabarito.exists():
            print(f"! Gabarito ausente para {ano_label}, pulando")
            continue
        pares.append((prova, gabarito, ano_label))

    for prova, gabarito, ano_label in pares:
        print(f"Parsing {ano_label}...")
        qs = parse_prova(prova, gabarito, ano_label)
        print(f"  {len(qs)} questões extraídas")
        out.extend(qs)
    return out


if __name__ == "__main__":
    from .load import save_bank
    from .schema import QuestionBank

    qs = parse_all()
    bank = QuestionBank(version="1", questions=qs)
    save_bank(bank)
    print(f"\nBanco salvo com {len(qs)} questões em data/questions.json")
