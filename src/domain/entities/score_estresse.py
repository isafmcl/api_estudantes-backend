"""Entidades ScoreEstresse e Alerta (DAS §4.3)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from src.domain.value_objects.enums import NivelEstresse, TipoAlerta


@dataclass
class DetalheSubScore:
    """Sub-score de uma variável específica dentro do cálculo total."""

    sub_score: int
    peso: int


@dataclass
class ScoreEstresse:
    """Resultado do cálculo de estresse para um dia (RN-001).

    Inclui o score total (0-100), o nível classificatório e o detalhamento
    por variável, permitindo que a UI mostre o que mais contribuiu.
    """

    usuario_id: int
    data: date
    score: Optional[int]
    nivel: NivelEstresse
    detalhes: dict[str, DetalheSubScore] = field(default_factory=dict)
    percentual_dados_registrados: int = 0
    id: Optional[int] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)

    @property
    def dados_suficientes(self) -> bool:
        return self.score is not None

    @property
    def is_critico_ou_elevado(self) -> bool:
        """Útil para regra RN-003 de detecção de burnout."""
        return self.nivel in (NivelEstresse.ELEVADO, NivelEstresse.CRITICO)


@dataclass
class Alerta:
    """Alerta gerado pelo sistema para o usuário (US14, RN-003)."""

    usuario_id: int
    tipo: TipoAlerta
    titulo: str
    mensagem: str
    id: Optional[int] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)
    lido: bool = False
