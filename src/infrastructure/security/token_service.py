"""Implementação concreta de ITokenService usando python-jose (JWT)."""

from datetime import datetime, timedelta

from jose import JWTError, jwt

from src.domain.interfaces.i_security import ITokenService, TokenInvalidoError


class JwtTokenService(ITokenService):
    """Emite e valida tokens JWT. Secret e expiração injetados via construtor."""

    def __init__(self, secret: str, algorithm: str = "HS256", expire_minutes: int = 1440) -> None:
        if not secret:
            raise ValueError("JWT secret é obrigatório.")
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def gerar(self, usuario_id: int) -> str:
        exp = datetime.utcnow() + timedelta(minutes=self._expire_minutes)
        payload = {"sub": str(usuario_id), "exp": exp}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def validar(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            sub = payload.get("sub")
            if sub is None:
                raise TokenInvalidoError("Token sem subject.")
            return int(sub)
        except JWTError as exc:
            raise TokenInvalidoError(f"Token inválido: {exc}") from exc
