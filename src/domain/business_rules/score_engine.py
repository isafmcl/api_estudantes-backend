"""ScoreEngine (RN-001): cálculo ponderado do nível de estresse.

Implementação seguindo OCP — cada fator é uma estratégia independente.
Adicionar nova variável ao cálculo não requer modificar o ScoreEngine,
apenas registrar um novo FatorEstresse na lista.

Pesos refletem RN-001 (composição do score) e RN-004 (peso elevado do sono).
RN-005 (sono < 6h crítico) é tratada dentro do FatorSono.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from src.domain.entities.registro_diario import (
    RegistroAlimentacao,
    RegistroAtividadeAcademica,
    RegistroAtividadeFisica,
    RegistroHumor,
    RegistroInteracaoSocial,
    RegistroSono,
)
from src.domain.entities.score_estresse import DetalheSubScore, ScoreEstresse
from src.domain.value_objects.enums import (
    NivelAtividadeFisica,
    NivelEstresse,
    NivelHumor,
    QualidadeAlimentacao,
    QualidadeInteracaoSocial,
    QualidadeSono,
)
from src.domain.value_objects.pesos import PesosVariaveis, PESOS_PADRAO


# ───── DTO de entrada para o cálculo ─────────────────────────────────────────


class DadosDoDia:
    """Container imutável com todos os registros do dia (pode ter nulls)."""

    def __init__(
        self,
        humor: Optional[RegistroHumor] = None,
        sono: Optional[RegistroSono] = None,
        atividades_academicas: Optional[list[RegistroAtividadeAcademica]] = None,
        alimentacao: Optional[RegistroAlimentacao] = None,
        atividade_fisica: Optional[RegistroAtividadeFisica] = None,
        interacao_social: Optional[RegistroInteracaoSocial] = None,
    ) -> None:
        self.humor = humor
        self.sono = sono
        self.atividades_academicas = atividades_academicas or []
        self.alimentacao = alimentacao
        self.atividade_fisica = atividade_fisica
        self.interacao_social = interacao_social


# ───── Interface comum de cada fator (Strategy + OCP) ────────────────────────


class FatorEstresse(ABC):
    """Estratégia abstrata: cada variável calcula seu próprio sub-score 0-100."""

    nome: str
    peso: int

    @abstractmethod
    def aplicavel(self, dados: DadosDoDia) -> bool:
        """Retorna True se os dados contêm informação para este fator."""

    @abstractmethod
    def sub_score(self, dados: DadosDoDia) -> int:
        """Sub-score 0-100, onde 0 = nenhum estresse, 100 = estresse máximo."""


# ───── Implementações concretas ──────────────────────────────────────────────


class FatorHumor(FatorEstresse):
    """Mapeia humor 1-5 em sub-score invertido (humor pior → estresse maior)."""

    nome = "humor"

    def __init__(self, peso: int) -> None:
        self.peso = peso
        self._mapa = {
            NivelHumor.MUITO_RUIM: 100,
            NivelHumor.RUIM: 75,
            NivelHumor.REGULAR: 50,
            NivelHumor.BOM: 25,
            NivelHumor.MUITO_BOM: 0,
        }

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return dados.humor is not None

    def sub_score(self, dados: DadosDoDia) -> int:
        return self._mapa[dados.humor.nivel]


class FatorSono(FatorEstresse):
    """Combina duração e qualidade do sono. RN-004 + RN-005."""

    nome = "sono"

    def __init__(self, peso: int) -> None:
        self.peso = peso
        self._mapa_qualidade = {
            QualidadeSono.RUIM: 50,
            QualidadeSono.REGULAR: 25,
            QualidadeSono.OTIMO: 0,
        }

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return dados.sono is not None

    def sub_score(self, dados: DadosDoDia) -> int:
        sono = dados.sono
        score = 0

        # Penalidade por duração
        horas = sono.horas_dormidas
        if horas < 4:
            score += 50
        elif horas < 6:  # RN-005
            score += 40
        elif horas < 7:
            score += 20
        elif horas > 9:
            score += 10  # excesso pode indicar problema

        # RN-004: qualidade pesa mais que duração no sub-score interno
        score += self._mapa_qualidade[sono.qualidade]

        if sono.houve_interrupcoes:
            score += 10

        # RN-005: garantia de elevação crítica
        if sono.sono_insuficiente:
            score = max(score, 60)

        return min(score, 100)


class FatorAtividadeAcademica(FatorEstresse):
    """Carga acadêmica progressiva: mais tempo = mais estresse."""

    nome = "atividade_academica"

    def __init__(self, peso: int) -> None:
        self.peso = peso

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return len(dados.atividades_academicas) > 0

    def sub_score(self, dados: DadosDoDia) -> int:
        total = sum(a.tempo_minutos for a in dados.atividades_academicas)
        if total <= 60:
            return 10
        if total <= 120:
            return 30
        if total <= 240:
            return 55
        if total <= 360:
            return 75
        return 95


class FatorAlimentacao(FatorEstresse):
    """Alimentação ruim eleva estresse."""

    nome = "alimentacao"

    def __init__(self, peso: int) -> None:
        self.peso = peso
        self._mapa = {
            QualidadeAlimentacao.RUIM: 80,
            QualidadeAlimentacao.REGULAR: 40,
            QualidadeAlimentacao.OTIMA: 0,
        }

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return dados.alimentacao is not None

    def sub_score(self, dados: DadosDoDia) -> int:
        return self._mapa[dados.alimentacao.qualidade]


class FatorAtividadeFisica(FatorEstresse):
    """Exercício REDUZ estresse — score invertido."""

    nome = "atividade_fisica"

    def __init__(self, peso: int) -> None:
        self.peso = peso
        self._mapa = {
            NivelAtividadeFisica.NULA: 80,
            NivelAtividadeFisica.LEVE: 40,
            NivelAtividadeFisica.MODERADA: 10,
            NivelAtividadeFisica.PESADA: 0,
        }

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return dados.atividade_fisica is not None

    def sub_score(self, dados: DadosDoDia) -> int:
        return self._mapa[dados.atividade_fisica.nivel]


class FatorInteracaoSocial(FatorEstresse):
    """Isolamento social eleva estresse."""

    nome = "interacao_social"

    def __init__(self, peso: int) -> None:
        self.peso = peso
        self._mapa = {
            QualidadeInteracaoSocial.NULA: 80,
            QualidadeInteracaoSocial.RUIM: 60,
            QualidadeInteracaoSocial.NEUTRA: 30,
            QualidadeInteracaoSocial.BOA: 0,
        }

    def aplicavel(self, dados: DadosDoDia) -> bool:
        return dados.interacao_social is not None

    def sub_score(self, dados: DadosDoDia) -> int:
        return self._mapa[dados.interacao_social.qualidade]


# ───── ScoreEngine: orquestrador ─────────────────────────────────────────────


class ScoreEngine:
    """RN-001: motor de cálculo do score de estresse ponderado.

    Composição via Strategy: a lista de fatores pode ser substituída em testes
    ou estendida sem modificar esta classe (OCP).
    """

    def __init__(self, pesos: PesosVariaveis | None = None) -> None:
        p = pesos or PESOS_PADRAO
        self._fatores: list[FatorEstresse] = [
            FatorHumor(p.humor),
            FatorSono(p.sono),
            FatorAtividadeAcademica(p.atividade_academica),
            FatorAlimentacao(p.alimentacao),
            FatorAtividadeFisica(p.atividade_fisica),
            FatorInteracaoSocial(p.interacao_social),
        ]

    def calcular(self, usuario_id: int, data, dados: DadosDoDia) -> ScoreEstresse:
        """Calcula score 0-100. Score = None se nenhum fator for aplicável."""
        soma_ponderada = 0
        pesos_usados = 0
        detalhes: dict[str, DetalheSubScore] = {}

        for fator in self._fatores:
            if not fator.aplicavel(dados):
                continue
            sub = fator.sub_score(dados)
            detalhes[fator.nome] = DetalheSubScore(sub_score=sub, peso=fator.peso)
            soma_ponderada += sub * fator.peso
            pesos_usados += fator.peso

        score = round(soma_ponderada / pesos_usados) if pesos_usados > 0 else None
        nivel = self._classificar(score)

        return ScoreEstresse(
            usuario_id=usuario_id,
            data=data,
            score=score,
            nivel=nivel,
            detalhes=detalhes,
            percentual_dados_registrados=pesos_usados,
        )

    @staticmethod
    def _classificar(score: Optional[int]) -> NivelEstresse:
        if score is None:
            return NivelEstresse.INDEFINIDO
        if score <= 25:
            return NivelEstresse.BAIXO
        if score <= 50:
            return NivelEstresse.MODERADO
        if score <= 70:
            return NivelEstresse.ELEVADO
        return NivelEstresse.CRITICO
