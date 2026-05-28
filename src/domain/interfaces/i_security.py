"""Ports de segurança: hashing e tokens (DAS §4.3 - auth.app)."""

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Port para hashing de senhas. Implementação concreta usa bcrypt/argon2."""

    @abstractmethod
    def hash(self, senha: str) -> str: ...

    @abstractmethod
    def verificar(self, senha: str, hash_armazenado: str) -> bool: ...


class ITokenService(ABC):
    """Port para emissão/validação de tokens JWT."""

    @abstractmethod
    def gerar(self, usuario_id: int) -> str: ...

    @abstractmethod
    def validar(self, token: str) -> int:
        """Retorna usuario_id ou lança TokenInvalidoError."""


class TokenInvalidoError(Exception):
    """Disparado quando o token JWT é inválido ou expirado."""
