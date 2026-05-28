"""PesoVariavel: coeficientes ponderados no cálculo do score (RN-004/005, DAS §4.3)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PesosVariaveis:
    """Pesos relativos de cada variável no score de estresse (RN-001).

    Os pesos refletem o impacto de cada dimensão no nível de estresse total.
    RN-004: a qualidade do sono tem peso elevado.
    A soma dos pesos é 100, mas o score é normalizado pelos pesos efetivamente
    presentes (dados parciais geram score parcial).
    """

    humor: int = 25
    sono: int = 25
    atividade_academica: int = 20
    alimentacao: int = 10
    atividade_fisica: int = 10
    interacao_social: int = 10

    def __post_init__(self) -> None:
        total = (
            self.humor
            + self.sono
            + self.atividade_academica
            + self.alimentacao
            + self.atividade_fisica
            + self.interacao_social
        )
        if total != 100:
            raise ValueError(f"Soma dos pesos deve ser 100, recebido {total}.")


PESOS_PADRAO = PesosVariaveis()
