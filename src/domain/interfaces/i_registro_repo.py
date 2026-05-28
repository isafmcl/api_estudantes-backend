"""IRegistroRepo: contratos de persistência dos registros diários (DAS §4.3)."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from src.domain.entities.registro_diario import (
    RegistroAlimentacao,
    RegistroAtividadeAcademica,
    RegistroAtividadeFisica,
    RegistroHumor,
    RegistroInteracaoSocial,
    RegistroSono,
)
from src.domain.value_objects.periodo_datas import PeriodoDatas


class IHumorRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroHumor]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroHumor]: ...

    @abstractmethod
    def salvar(self, registro: RegistroHumor) -> RegistroHumor: ...


class ISonoRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroSono]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroSono]: ...

    @abstractmethod
    def salvar(self, registro: RegistroSono) -> RegistroSono: ...


class IAtividadeAcademicaRepo(ABC):
    @abstractmethod
    def buscar_por_id(self, usuario_id: int, registro_id: int) -> Optional[RegistroAtividadeAcademica]: ...

    @abstractmethod
    def listar_do_dia(self, usuario_id: int, dia: date) -> list[RegistroAtividadeAcademica]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroAtividadeAcademica]: ...

    @abstractmethod
    def salvar(self, registro: RegistroAtividadeAcademica) -> RegistroAtividadeAcademica: ...

    @abstractmethod
    def remover(self, usuario_id: int, registro_id: int) -> bool: ...


class IAlimentacaoRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroAlimentacao]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroAlimentacao]: ...

    @abstractmethod
    def salvar(self, registro: RegistroAlimentacao) -> RegistroAlimentacao: ...


class IAtividadeFisicaRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroAtividadeFisica]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroAtividadeFisica]: ...

    @abstractmethod
    def salvar(self, registro: RegistroAtividadeFisica) -> RegistroAtividadeFisica: ...


class IInteracaoSocialRepo(ABC):
    @abstractmethod
    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroInteracaoSocial]: ...

    @abstractmethod
    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroInteracaoSocial]: ...

    @abstractmethod
    def salvar(self, registro: RegistroInteracaoSocial) -> RegistroInteracaoSocial: ...
