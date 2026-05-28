"""Router de autenticação (US01, US02)."""

from fastapi import APIRouter, HTTPException, status

from src.application.auth.auth_service import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)
from src.application.dtos import CadastroDTO, LoginDTO
from src.infrastructure.http.dependencies.providers import (
    AuthServiceDep,
    UsuarioAtualDep,
)
from src.infrastructure.http.schemas.schemas import (
    CadastroRequest,
    LoginRequest,
    TokenResponse,
    UsuarioResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro de novo usuário (US01)",
)
def register(req: CadastroRequest, auth: AuthServiceDep) -> UsuarioResponse:
    try:
        resp = auth.cadastrar(CadastroDTO(nome=req.nome, email=req.email, senha=req.senha))
    except EmailJaCadastradoError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UsuarioResponse(id=resp.id, nome=resp.nome, email=resp.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login e emissão de JWT (US02)",
)
def login(req: LoginRequest, auth: AuthServiceDep) -> TokenResponse:
    try:
        token = auth.autenticar(LoginDTO(email=req.email, senha=req.senha))
    except CredenciaisInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return TokenResponse(access_token=token.access_token, token_type=token.token_type)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Dados do usuário autenticado",
)
def me(usuario: UsuarioAtualDep) -> UsuarioResponse:
    return UsuarioResponse(id=usuario.id, nome=usuario.nome, email=usuario.email)
