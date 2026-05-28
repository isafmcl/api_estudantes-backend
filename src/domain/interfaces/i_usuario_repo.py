"""IUsuarioRepo: contrato de persistência de usuários (DAS §4.3 interfaces)."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.usuario import Usuario


class IUsuarioRepo(ABC):
    """Port: implementação concreta vive em infrastructure/persistence."""

    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]: ...

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Usuario]: ...

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario: ...
