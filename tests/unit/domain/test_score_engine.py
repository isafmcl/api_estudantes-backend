"""Testes unitários da regra de negócio RN-001 (ScoreEngine).

Domínio é puro: nenhum mock de banco ou framework necessário.
Esta característica é o teste do desacoplamento da arquitetura.
"""

from datetime import date

import pytest

from src.domain.business_rules.score_engine import (
    DadosDoDia,
    ScoreEngine,
)
from src.domain.entities.registro_diario import (
    RegistroAlimentacao,
    RegistroAtividadeAcademica,
    RegistroAtividadeFisica,
    RegistroHumor,
    RegistroInteracaoSocial,
    RegistroSono,
)
from src.domain.value_objects.enums import (
    NivelAtividadeFisica,
    NivelEstresse,
    NivelHumor,
    QualidadeAlimentacao,
    QualidadeInteracaoSocial,
    QualidadeSono,
)


HOJE = date(2026, 5, 27)


@pytest.fixture
def engine() -> ScoreEngine:
    return ScoreEngine()


# ── Casos de borda: sem dados ────────────────────────────────────────────────


def test_sem_dados_retorna_score_none_e_indefinido(engine: ScoreEngine) -> None:
    resultado = engine.calcular(usuario_id=1, data=HOJE, dados=DadosDoDia())
    assert resultado.score is None
    assert resultado.nivel == NivelEstresse.INDEFINIDO
    assert resultado.dados_suficientes is False


# ── RN-001: cálculo ponderado ────────────────────────────────────────────────


def test_humor_muito_bom_sozinho_da_score_zero(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        humor=RegistroHumor(usuario_id=1, data=HOJE, nivel=NivelHumor.MUITO_BOM)
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score == 0
    assert resultado.nivel == NivelEstresse.BAIXO


def test_humor_muito_ruim_sozinho_da_score_critico(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        humor=RegistroHumor(usuario_id=1, data=HOJE, nivel=NivelHumor.MUITO_RUIM)
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score == 100
    assert resultado.nivel == NivelEstresse.CRITICO


# ── RN-005: sono < 6h eleva criticamente ────────────────────────────────────


def test_rn005_sono_insuficiente_eleva_score(engine: ScoreEngine) -> None:
    """Sono < 6h deve gerar sub_score >= 60 mesmo com qualidade regular."""
    dados = DadosDoDia(
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=5.0, qualidade=QualidadeSono.REGULAR
        )
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score is not None
    assert resultado.score >= 60
    assert "sono" in resultado.detalhes
    assert resultado.detalhes["sono"].sub_score >= 60


def test_rn005_sono_de_8h_otimo_da_score_baixo(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=8.0, qualidade=QualidadeSono.OTIMO
        )
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score == 0
    assert resultado.nivel == NivelEstresse.BAIXO


# ── RN-004: qualidade do sono pesa mais que duração ─────────────────────────


def test_rn004_qualidade_sono_pesa_mais_que_duracao(engine: ScoreEngine) -> None:
    """8h de sono RUIM deve gerar score > 8h de sono ÓTIMO."""
    dados_ruim = DadosDoDia(
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=8.0, qualidade=QualidadeSono.RUIM
        )
    )
    dados_otimo = DadosDoDia(
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=8.0, qualidade=QualidadeSono.OTIMO
        )
    )
    s_ruim = engine.calcular(1, HOJE, dados_ruim).score
    s_otimo = engine.calcular(1, HOJE, dados_otimo).score
    assert s_ruim is not None and s_otimo is not None
    assert s_ruim > s_otimo


# ── Carga acadêmica acumulada ────────────────────────────────────────────────


def test_atividades_academicas_somam_e_aumentam_score(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        atividades_academicas=[
            RegistroAtividadeAcademica(
                usuario_id=1, data=HOJE, descricao="Estudo", tempo_minutos=240
            ),
            RegistroAtividadeAcademica(
                usuario_id=1, data=HOJE, descricao="Trabalho", tempo_minutos=180
            ),
        ]
    )
    resultado = engine.calcular(1, HOJE, dados)
    # Total = 420 min → entre 360 e infinito → sub_score = 95
    assert resultado.detalhes["atividade_academica"].sub_score == 95


# ── Atividade física reduz estresse ─────────────────────────────────────────


def test_atividade_fisica_pesada_da_sub_score_zero(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        atividade_fisica=RegistroAtividadeFisica(
            usuario_id=1, data=HOJE, nivel=NivelAtividadeFisica.PESADA
        )
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.detalhes["atividade_fisica"].sub_score == 0


def test_atividade_fisica_nula_eleva_sub_score(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        atividade_fisica=RegistroAtividadeFisica(
            usuario_id=1, data=HOJE, nivel=NivelAtividadeFisica.NULA
        )
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.detalhes["atividade_fisica"].sub_score == 80


# ── Combinação multi-fator ─────────────────────────────────────────────────


def test_dados_completos_dia_pessimo_da_critico(engine: ScoreEngine) -> None:
    """Cenário de dia ruim em todas as dimensões → score crítico."""
    dados = DadosDoDia(
        humor=RegistroHumor(usuario_id=1, data=HOJE, nivel=NivelHumor.MUITO_RUIM),
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=4.0, qualidade=QualidadeSono.RUIM,
            houve_interrupcoes=True,
        ),
        atividades_academicas=[
            RegistroAtividadeAcademica(
                usuario_id=1, data=HOJE, descricao="Estudo", tempo_minutos=480
            ),
        ],
        alimentacao=RegistroAlimentacao(
            usuario_id=1, data=HOJE, qualidade=QualidadeAlimentacao.RUIM
        ),
        atividade_fisica=RegistroAtividadeFisica(
            usuario_id=1, data=HOJE, nivel=NivelAtividadeFisica.NULA
        ),
        interacao_social=RegistroInteracaoSocial(
            usuario_id=1, data=HOJE, qualidade=QualidadeInteracaoSocial.NULA
        ),
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score is not None
    assert resultado.score > 70
    assert resultado.nivel == NivelEstresse.CRITICO


def test_dados_completos_dia_excelente_da_baixo(engine: ScoreEngine) -> None:
    dados = DadosDoDia(
        humor=RegistroHumor(usuario_id=1, data=HOJE, nivel=NivelHumor.MUITO_BOM),
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=8.0, qualidade=QualidadeSono.OTIMO
        ),
        atividades_academicas=[
            RegistroAtividadeAcademica(
                usuario_id=1, data=HOJE, descricao="Estudo", tempo_minutos=60
            ),
        ],
        alimentacao=RegistroAlimentacao(
            usuario_id=1, data=HOJE, qualidade=QualidadeAlimentacao.OTIMA
        ),
        atividade_fisica=RegistroAtividadeFisica(
            usuario_id=1, data=HOJE, nivel=NivelAtividadeFisica.MODERADA
        ),
        interacao_social=RegistroInteracaoSocial(
            usuario_id=1, data=HOJE, qualidade=QualidadeInteracaoSocial.BOA
        ),
    )
    resultado = engine.calcular(1, HOJE, dados)
    assert resultado.score is not None
    assert resultado.score <= 25
    assert resultado.nivel == NivelEstresse.BAIXO


# ── Normalização por dados parciais ─────────────────────────────────────────


def test_dados_parciais_normalizam_score_corretamente(engine: ScoreEngine) -> None:
    """Quando só metade dos fatores tem dados, score é normalizado por eles."""
    dados = DadosDoDia(
        humor=RegistroHumor(usuario_id=1, data=HOJE, nivel=NivelHumor.REGULAR),
        sono=RegistroSono(
            usuario_id=1, data=HOJE, horas_dormidas=7.0, qualidade=QualidadeSono.REGULAR
        ),
    )
    resultado = engine.calcular(1, HOJE, dados)
    # humor=50 (×25) + sono=25 (×25) = 1875 / 50 = 37.5 → arredonda para 38
    assert resultado.score == 38
    assert resultado.nivel == NivelEstresse.MODERADO
    assert resultado.percentual_dados_registrados == 50
