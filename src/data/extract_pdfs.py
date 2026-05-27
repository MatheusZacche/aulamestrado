"""Extract raw text from PPGI PDFs into .txt for inspection.

Run: python src/data/extract_pdfs.py
"""
from __future__ import annotations
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "exams" / "raw"
TEXT_DIR = ROOT / "data" / "exams" / "text"
TEXT_DIR.mkdir(parents=True, exist_ok=True)


def extract(pdf_path: Path) -> str:
    out_lines: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            out_lines.append(f"\n=== PAGE {i} ===\n")
            text = page.extract_text() or ""
            out_lines.append(text)
    return "\n".join(out_lines)


def main() -> None:
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    for pdf in pdfs:
        target = TEXT_DIR / f"{pdf.stem}.txt"
        print(f"Extracting {pdf.name} -> {target.name}")
        target.write_text(extract(pdf), encoding="utf-8")
    print(f"Done. {len(pdfs)} PDFs extracted to {TEXT_DIR}")


if __name__ == "__main__":
    main()
