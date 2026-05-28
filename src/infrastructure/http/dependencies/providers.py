"""Providers de dependências para o FastAPI.

São funções que o FastAPI invoca em cada requisição para injetar
dependências nos endpoints. Usam o Container singleton.
"""

from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.application.auth.auth_service import (
    AuthService,
    CredenciaisInvalidasError,
)
from src.application.dtos import UsuarioResponseDTO
from src.application.estresse.alerta_service import AlertaService
from src.application.estresse.estresse_service import EstresseService
from src.application.registro.registro_service import RegistroService
from src.domain.interfaces.i_security import TokenInvalidoError

# Singletons inicializados em main.py
_container = None
_session_factory = None


def configurar(container, session_factory) -> None:
    """Configura os singletons. Chamado uma vez no startup."""
    global _container, _session_factory
    _container = container
    _session_factory = session_factory


def get_session() -> Generator[Session, None, None]:
    """Provê sessão do banco por requisição. Fecha automaticamente ao final."""
    if _session_factory is None:
        raise RuntimeError("Dependências não configuradas. Chame configurar() no startup.")
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


# ───── Services ─────────────────────────────────────────────────────────────


def get_auth_service(session: SessionDep) -> AuthService:
    return _container.construir_auth_service(session)


def get_registro_service(session: SessionDep) -> RegistroService:
    return _container.construir_registro_service(session)


def get_estresse_service(session: SessionDep) -> EstresseService:
    return _container.construir_estresse_service(session)


def get_alerta_service(session: SessionDep) -> AlertaService:
    return _container.construir_alerta_service(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
RegistroServiceDep = Annotated[RegistroService, Depends(get_registro_service)]
EstresseServiceDep = Annotated[EstresseService, Depends(get_estresse_service)]
AlertaServiceDep = Annotated[AlertaService, Depends(get_alerta_service)]


# ───── Autenticação ─────────────────────────────────────────────────────────


_bearer = HTTPBearer(auto_error=False)


def get_usuario_atual(
    auth: AuthServiceDep,
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> UsuarioResponseDTO:
    """Resolve o usuário autenticado a partir do header Authorization: Bearer."""
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return auth.usuario_do_token(credenciais.credentials)
    except (TokenInvalidoError, CredenciaisInvalidasError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


UsuarioAtualDep = Annotated[UsuarioResponseDTO, Depends(get_usuario_atual)]
