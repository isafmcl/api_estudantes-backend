"""Implementação concreta de IPasswordHasher usando passlib + bcrypt."""

from passlib.context import CryptContext

from src.domain.interfaces.i_security import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Hashing seguro com bcrypt. Cost factor padrão (12) é adequado."""

    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, senha: str) -> str:
        if not senha:
            raise ValueError("Senha não pode estar vazia.")
        return self._ctx.hash(senha)

    def verificar(self, senha: str, hash_armazenado: str) -> bool:
        try:
            return self._ctx.verify(senha, hash_armazenado)
        except Exception:  # noqa: BLE001
            return False
