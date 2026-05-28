"""Entidade RegistroDiario: agregação dos dados de um dia (DAS §4.3)."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.domain.value_objects.enums import (
    NivelAtividadeFisica,
    NivelHumor,
    QualidadeAlimentacao,
    QualidadeInteracaoSocial,
    QualidadeSono,
)


@dataclass
class RegistroHumor:
    """Snapshot de humor do dia (US03)."""

    usuario_id: int
    data: date
    nivel: NivelHumor
    observacao: Optional[str] = None
    id: Optional[int] = None


@dataclass
class RegistroSono:
    """Snapshot de sono do dia (US05). RN-004: qualidade pesa mais que duração."""

    usuario_id: int
    data: date
    horas_dormidas: float
    qualidade: QualidadeSono
    houve_interrupcoes: bool = False
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not 0 <= self.horas_dormidas <= 24:
            raise ValueError("Horas dormidas deve estar entre 0 e 24.")

    @property
    def sono_insuficiente(self) -> bool:
        """RN-005: sono abaixo de 6h é considerado insuficiente."""
        return self.horas_dormidas < 6


@dataclass
class RegistroAtividadeAcademica:
    """Atividade acadêmica do dia (US04). Pode haver várias por dia."""

    usuario_id: int
    data: date
    descricao: str
    tempo_minutos: int
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not 1 <= self.tempo_minutos <= 1440:
            raise ValueError("Tempo em minutos deve estar entre 1 e 1440.")
        if not self.descricao.strip():
            raise ValueError("Descrição é obrigatória.")


@dataclass
class RegistroAlimentacao:
    """Alimentação do dia (US06)."""

    usuario_id: int
    data: date
    qualidade: QualidadeAlimentacao
    id: Optional[int] = None


@dataclass
class RegistroAtividadeFisica:
    """Atividade física do dia (US07)."""

    usuario_id: int
    data: date
    nivel: NivelAtividadeFisica
    id: Optional[int] = None


@dataclass
class RegistroInteracaoSocial:
    """Interação social do dia (US08)."""

    usuario_id: int
    data: date
    qualidade: QualidadeInteracaoSocial
    teve_interacao: bool = True
    id: Optional[int] = None
