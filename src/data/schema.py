"""Modelos canônicos de questão e validação.

O formato JSON do banco é uma lista de Question. Cada questão tem:
- identificador determinístico
- conteúdo (enunciado + alternativas)
- metadados (eixo, subtópicos, origem, dificuldade)
- explicações por alternativa
- resultado de validação (se passou pelo agente)
"""
from __future__ import annotations

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator


AlternativeKey = Literal["a", "b", "c", "d", "e"]


class Origem(str, Enum):
    oficial = "oficial"
    gerada_validada = "gerada_validada"
    gerada_revisada = "gerada_revisada"
    gerada_rascunho = "gerada_rascunho"


class Dificuldade(str, Enum):
    facil = "facil"
    medio = "medio"
    dificil = "dificil"


class Alternativa(BaseModel):
    chave: AlternativeKey
    texto: str
    explicacao: str = Field(
        default="",
        description="Por que esta alternativa está certa ou errada. Preenchido pelo agente validador.",
    )


class ValidacaoResult(BaseModel):
    validado: bool = False
    confianca: float = Field(default=0.0, ge=0.0, le=1.0)
    raciocinio: str = ""
    flags: list[str] = Field(default_factory=list)
    modelo: str = ""
    data: str = ""


class Question(BaseModel):
    id: str = Field(description="Identificador único, ex: oficial_2026-1_q01 ou gerada_0001")
    origem: Origem
    eixo: Literal["raciocinio_logico", "programacao", "paradigmas", "estruturas_dados"]
    subtopicos: list[str] = Field(default_factory=list)
    ano: str | None = Field(default=None, description="Ex: 2026-1; None para geradas")
    numero_na_prova: int | None = None
    enunciado: str
    alternativas: list[Alternativa] = Field(min_length=2, max_length=5)
    gabarito: AlternativeKey
    dificuldade: Dificuldade = Dificuldade.medio
    anulada: bool = False
    motivo_anulacao: str = ""
    tags: list[str] = Field(default_factory=list)
    validacao: ValidacaoResult = Field(default_factory=ValidacaoResult)

    @field_validator("alternativas")
    @classmethod
    def chaves_unicas(cls, v: list[Alternativa]) -> list[Alternativa]:
        chaves = [a.chave for a in v]
        if len(chaves) != len(set(chaves)):
            raise ValueError("alternativas com chaves duplicadas")
        return v


class QuestionBank(BaseModel):
    version: str = "1"
    questions: list[Question]


def empty_bank() -> QuestionBank:
    return QuestionBank(version="1", questions=[])
