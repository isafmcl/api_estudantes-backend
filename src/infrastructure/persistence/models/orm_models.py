"""Models SQLAlchemy (infraestrutura).

ATENÇÃO: estas classes NUNCA devem vazar para domain/ ou application/.
Repositórios fazem a tradução entre Model (ORM) e Entity (domínio).
"""

from datetime import date as date_type
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HumorModel(Base):
    __tablename__ = "humor"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_humor_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SonoModel(Base):
    __tablename__ = "sono"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_sono_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    horas_dormidas: Mapped[float] = mapped_column(Float, nullable=False)
    qualidade: Mapped[str] = mapped_column(String, nullable=False)
    houve_interrupcoes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AtividadeAcademicaModel(Base):
    __tablename__ = "atividade_academica"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    tempo_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlimentacaoModel(Base):
    __tablename__ = "alimentacao"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_alimentacao_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    qualidade: Mapped[str] = mapped_column(String, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AtividadeFisicaModel(Base):
    __tablename__ = "atividade_fisica"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_atividade_fisica_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    nivel: Mapped[str] = mapped_column(String, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InteracaoSocialModel(Base):
    __tablename__ = "interacao_social"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_interacao_social_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    qualidade: Mapped[str] = mapped_column(String, nullable=False)
    teve_interacao: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScoreEstresseModel(Base):
    __tablename__ = "score_estresse"
    __table_args__ = (UniqueConstraint("usuario_id", "data", name="uq_score_usuario_data"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nivel: Mapped[str] = mapped_column(String, nullable=False)
    percentual_dados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlertaModel(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    lido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
