"""LimiteDiario (RN-002): garante no máximo um registro por dia por tipo."""

from datetime import date
from typing import Optional


class LimiteDiarioExcedido(Exception):
    """Disparado quando um segundo registro do mesmo tipo é tentado no mesmo dia."""

    def __init__(self, tipo: str, dia: date) -> None:
        super().__init__(f"Já existe um registro de {tipo} para {dia}.")
        self.tipo = tipo
        self.dia = dia


class LimiteDiario:
    """RN-002: valida unicidade de registros por dia (exceto atividade acadêmica)."""

    @staticmethod
    def garantir_unico(existente: Optional[object], tipo: str, dia: date) -> None:
        if existente is not None:
            raise LimiteDiarioExcedido(tipo=tipo, dia=dia)
