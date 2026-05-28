"""Schemas Pydantic para a camada HTTP.

Validação de entrada/saída no boundary HTTP. NÃO são entidades de domínio.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ───── Auth ─────────────────────────────────────────────────────────────────


class CadastroRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str


# ───── Registros ────────────────────────────────────────────────────────────


class HumorRequest(BaseModel):
    data: date
    nivel: int = Field(..., ge=1, le=5)
    observacao: Optional[str] = None


class HumorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    nivel: int
    observacao: Optional[str] = None


class SonoRequest(BaseModel):
    data: date
    horas_dormidas: float = Field(..., ge=0, le=24)
    qualidade: str = Field(..., pattern="^(ruim|regular|otimo)$")
    houve_interrupcoes: bool = False


class SonoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    horas_dormidas: float
    qualidade: str
    houve_interrupcoes: bool


class AtividadeAcademicaRequest(BaseModel):
    data: date
    descricao: str = Field(..., min_length=1, max_length=200)
    tempo_minutos: int = Field(..., ge=1, le=1440)


class AtividadeAcademicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    descricao: str
    tempo_minutos: int


class AlimentacaoRequest(BaseModel):
    data: date
    qualidade: str = Field(..., pattern="^(ruim|regular|otima)$")


class AlimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    qualidade: str


class AtividadeFisicaRequest(BaseModel):
    data: date
    nivel: str = Field(..., pattern="^(nula|leve|moderada|pesada)$")


class AtividadeFisicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    nivel: str


class InteracaoSocialRequest(BaseModel):
    data: date
    qualidade: str = Field(..., pattern="^(nula|ruim|neutra|boa)$")
    teve_interacao: bool = True


class InteracaoSocialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: date
    qualidade: str
    teve_interacao: bool


# ───── Score e Alerta ───────────────────────────────────────────────────────


class DetalheSubScoreSchema(BaseModel):
    sub_score: int
    peso: int


class ScoreResponse(BaseModel):
    data: date
    score: Optional[int]
    nivel: str
    detalhes: dict[str, DetalheSubScoreSchema]
    percentual_dados_registrados: int
    cor_indicativa: str
    emoji: str


class HistoricoItemResponse(BaseModel):
    data: date
    score: Optional[int]
    nivel: str


class AlertaBurnoutInfo(BaseModel):
    alerta: bool
    dias_consecutivos: Optional[int] = None
    mensagem: Optional[str] = None


class HistoricoResponse(BaseModel):
    historico: list[HistoricoItemResponse]
    alerta_burnout: AlertaBurnoutInfo


class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
    titulo: str
    mensagem: str
    lido: bool
    criado_em: datetime
