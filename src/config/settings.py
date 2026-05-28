"""Configuração via variáveis de ambiente (12-factor app).

Nenhum segredo hardcoded — tudo lido do ambiente.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Configurações da aplicação carregadas do ambiente."""

    # Database
    database_url: str
    # Security
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int
    # API
    api_title: str
    api_version: str
    cors_origins: list[str]
    debug: bool

    @classmethod
    def from_env(cls) -> "Settings":
        secret = os.getenv("JWT_SECRET")
        if not secret:
            raise RuntimeError(
                "JWT_SECRET não configurado. Defina a variável de ambiente antes de iniciar."
            )

        cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:19006")
        origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///./mindtrack.db"),
            jwt_secret=secret,
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "1440")),
            api_title=os.getenv("API_TITLE", "MindTrack API"),
            api_version=os.getenv("API_VERSION", "1.0.0"),
            cors_origins=origins,
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
