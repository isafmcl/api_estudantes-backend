"""Implementação SQLAlchemy do IUsuarioRepo.

Faz tradução bidirecional: ORM Model ↔ Domain Entity.
A camada de aplicação só conhece Usuario (entidade), nunca UsuarioModel.
"""

from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.usuario import Usuario
from src.domain.interfaces.i_usuario_repo import IUsuarioRepo
from src.infrastructure.persistence.models.orm_models import UsuarioModel


class UsuarioRepository(IUsuarioRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        model = self._session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return self._to_entity(model) if model else None

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        model = self._session.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        return self._to_entity(model) if model else None

    def salvar(self, usuario: Usuario) -> Usuario:
        model = UsuarioModel(
            email=usuario.email,
            nome=usuario.nome,
            senha_hash=usuario.senha_hash,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UsuarioModel) -> Usuario:
        return Usuario(
            id=model.id,
            email=model.email,
            nome=model.nome,
            senha_hash=model.senha_hash,
            criado_em=model.criado_em,
        )
