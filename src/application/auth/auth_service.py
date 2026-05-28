"""AuthService: orquestra cadastro, login e validação (DAS §4.3 auth.app).

Depende apenas das interfaces (DIP) — implementações concretas de hashing
e tokens são injetadas via construtor.
"""

from src.application.dtos import (
    CadastroDTO,
    LoginDTO,
    TokenResponseDTO,
    UsuarioResponseDTO,
)
from src.domain.entities.usuario import Usuario
from src.domain.interfaces.i_security import IPasswordHasher, ITokenService
from src.domain.interfaces.i_usuario_repo import IUsuarioRepo


class CredenciaisInvalidasError(Exception):
    """Email ou senha incorretos."""


class EmailJaCadastradoError(Exception):
    """Email já existe no sistema (US01)."""


class AuthService:
    """Caso de uso de autenticação. Recebe dependências por injeção (DIP)."""

    def __init__(
        self,
        usuario_repo: IUsuarioRepo,
        hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self._usuario_repo = usuario_repo
        self._hasher = hasher
        self._tokens = token_service

    def cadastrar(self, dto: CadastroDTO) -> UsuarioResponseDTO:
        """US01: cria novo usuário com senha hasheada."""
        if self._usuario_repo.buscar_por_email(dto.email):
            raise EmailJaCadastradoError(f"Email '{dto.email}' já cadastrado.")

        usuario = Usuario(
            nome=dto.nome.strip(),
            email=dto.email.lower().strip(),
            senha_hash=self._hasher.hash(dto.senha),
        )
        salvo = self._usuario_repo.salvar(usuario)
        return UsuarioResponseDTO(id=salvo.id, nome=salvo.nome, email=salvo.email)

    def autenticar(self, dto: LoginDTO) -> TokenResponseDTO:
        """US02: autentica e emite token JWT."""
        usuario = self._usuario_repo.buscar_por_email(dto.email.lower().strip())
        if not usuario or not self._hasher.verificar(dto.senha, usuario.senha_hash):
            raise CredenciaisInvalidasError("Email ou senha incorretos.")

        token = self._tokens.gerar(usuario.id)
        return TokenResponseDTO(access_token=token)

    def usuario_do_token(self, token: str) -> UsuarioResponseDTO:
        """Resolve token JWT em usuário. Usado pelo middleware de auth."""
        usuario_id = self._tokens.validar(token)
        usuario = self._usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise CredenciaisInvalidasError("Usuário do token não encontrado.")
        return UsuarioResponseDTO(id=usuario.id, nome=usuario.nome, email=usuario.email)
