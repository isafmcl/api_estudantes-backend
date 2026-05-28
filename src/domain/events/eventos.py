"""Eventos de domínio (DAS §4.3 - eventos).

Eventos imutáveis emitidos quando o estado do domínio muda. Quem produz
não conhece quem consome — desacoplamento via padrão Observer/Event.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class RegistroSalvo:
    """Emitido quando qualquer registro diário é persistido."""

    usuario_id: int
    tipo_registro: str
    data: date
    ocorrido_em: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ScoreAtualizado:
    """Emitido sempre que o score de estresse de um dia é recalculado."""

    usuario_id: int
    data: date
    score: Optional[int]
    nivel: str
    ocorrido_em: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class BurnoutDetectado:
    """RN-003: emitido quando o sistema detecta padrão de burnout."""

    usuario_id: int
    dias_consecutivos: int
    ocorrido_em: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AlertaGerado:
    """Emitido quando um novo alerta é gerado para um usuário."""

    usuario_id: int
    tipo: str
    titulo: str
    ocorrido_em: datetime = field(default_factory=datetime.utcnow)
