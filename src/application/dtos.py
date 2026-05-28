"""DTOs da camada de aplicação.

Objetos de transferência entre Apresentação (HTTP) e Aplicação.
Mantêm a entrada/saída desacoplada das entidades de domínio.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


# ───── Auth ─────────────────────────────────────────────────────────────────


@dataclass
class CadastroDTO:
    nome: str
    email: str
    senha: str


@dataclass
class LoginDTO:
    email: str
    senha: str


@dataclass
class TokenResponseDTO:
    access_token: str
    token_type: str = "bearer"


@dataclass
class UsuarioResponseDTO:
    id: int
    nome: str
    email: str


# ───── Registro ─────────────────────────────────────────────────────────────


@dataclass
class HumorDTO:
    data: date
    nivel: int
    observacao: Optional[str] = None


@dataclass
class SonoDTO:
    data: date
    horas_dormidas: float
    qualidade: str
    houve_interrupcoes: bool = False


@dataclass
class AtividadeAcademicaDTO:
    data: date
    descricao: str
    tempo_minutos: int


@dataclass
class AlimentacaoDTO:
    data: date
    qualidade: str


@dataclass
class AtividadeFisicaDTO:
    data: date
    nivel: str


@dataclass
class InteracaoSocialDTO:
    data: date
    qualidade: str
    teve_interacao: bool = True
