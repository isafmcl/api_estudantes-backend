"""IAlertService e IAlertaRepo: contratos para o sistema de alertas (DAS §4.3)."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.score_estresse import Alerta


class IAlertaRepo(ABC):
    @abstractmethod
    def listar_do_usuario(self, usuario_id: int, apenas_nao_lidos: bool = False) -> list[Alerta]: ...

    @abstractmethod
    def existe_recente(self, usuario_id: int, tipo: str, horas: int = 24) -> bool: ...

    @abstractmethod
    def salvar(self, alerta: Alerta) -> Alerta: ...

    @abstractmethod
    def marcar_como_lido(self, usuario_id: int, alerta_id: int) -> bool: ...


class IAlertaService(ABC):
    """Port para o caso de uso de emissão de alertas (DAS §4.3 - notif.app)."""

    @abstractmethod
    def avaliar_e_emitir(self, usuario_id: int) -> Optional[Alerta]: ...
