"""IScoreRepo: contrato para persistência de scores calculados (DAS §4.3)."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from src.domain.entities.score_estresse import ScoreEstresse
from src.domain.value_objects.periodo_datas import PeriodoDatas


class IScoreRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[ScoreEstresse]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: PeriodoDatas) -> list[ScoreEstresse]: ...

    @abstractmethod
    def salvar_ou_atualizar(self, score: ScoreEstresse) -> ScoreEstresse: ...
