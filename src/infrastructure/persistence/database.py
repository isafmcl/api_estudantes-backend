"""Configuração do banco de dados (SQLAlchemy + SQLite/PostgreSQL).

DAS §7: SQLite em desenvolvimento, PostgreSQL em produção.
A camada superior só conhece interfaces, não conhece esta configuração.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config.settings import Settings


class Base(DeclarativeBase):
    """Base para todos os models SQLAlchemy."""


def criar_engine_e_session(settings: Settings):
    """Fábrica de engine + SessionLocal a partir das settings."""
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=settings.debug,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal
