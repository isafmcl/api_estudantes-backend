"""Entidade Usuario: identidade e ciclo de vida no domínio (DAS §4.3)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """Usuário do sistema MindTrack.

    Entidade de domínio sem dependência de framework. A senha trafega aqui
    apenas em formato hash — o hashing fica na camada de infraestrutura.
    """

    email: str
    nome: str
    senha_hash: str
    id: Optional[int] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido.")
        if not self.nome.strip():
            raise ValueError("Nome não pode estar vazio.")
        if not self.senha_hash:
            raise ValueError("Senha hash é obrigatória.")
