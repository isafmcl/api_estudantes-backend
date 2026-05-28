"""PeriodoDatas: value object para intervalos temporais (DAS §4.3)."""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class PeriodoDatas:
    """Intervalo imutável de datas usado em filtros e relatórios."""

    inicio: date
    fim: date

    def __post_init__(self) -> None:
        if self.inicio > self.fim:
            raise ValueError("Data de início não pode ser posterior à data fim.")

    @classmethod
    def ultimos_n_dias(cls, n_dias: int, referencia: date | None = None) -> "PeriodoDatas":
        """Cria um período representando os últimos N dias até a referência."""
        if n_dias <= 0:
            raise ValueError("n_dias deve ser positivo.")
        fim = referencia or date.today()
        inicio = fim - timedelta(days=n_dias - 1)
        return cls(inicio=inicio, fim=fim)

    def contem(self, dia: date) -> bool:
        return self.inicio <= dia <= self.fim

    def dias(self) -> int:
        return (self.fim - self.inicio).days + 1
