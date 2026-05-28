"""Testes da regra RN-003 (AlertBurnout)."""

from datetime import date, timedelta

from src.domain.business_rules.alert_burnout import AlertBurnout
from src.domain.entities.score_estresse import ScoreEstresse
from src.domain.value_objects.enums import NivelEstresse


def _score(dia: date, valor: int | None) -> ScoreEstresse:
    nivel = NivelEstresse.INDEFINIDO if valor is None else NivelEstresse.ELEVADO
    return ScoreEstresse(usuario_id=1, data=dia, score=valor, nivel=nivel)


HOJE = date(2026, 5, 27)


def test_3_dias_consecutivos_acima_de_70_detecta_burnout() -> None:
    regra = AlertBurnout()
    historico_desc = [
        _score(HOJE, 75),
        _score(HOJE - timedelta(days=1), 80),
        _score(HOJE - timedelta(days=2), 85),
    ]
    assert regra.detectar(historico_desc) == 3


def test_2_dias_consecutivos_nao_detecta() -> None:
    regra = AlertBurnout()
    historico_desc = [
        _score(HOJE, 75),
        _score(HOJE - timedelta(days=1), 80),
    ]
    assert regra.detectar(historico_desc) is None


def test_sequencia_interrompida_nao_detecta() -> None:
    """RN-003 exige CONSECUTIVOS — 4 dias com 1 quebra no meio não conta."""
    regra = AlertBurnout()
    historico_desc = [
        _score(HOJE, 75),
        _score(HOJE - timedelta(days=1), 80),
        _score(HOJE - timedelta(days=2), 40),  # quebrou
        _score(HOJE - timedelta(days=3), 75),
    ]
    assert regra.detectar(historico_desc) is None


def test_scores_none_quebram_sequencia() -> None:
    regra = AlertBurnout()
    historico_desc = [
        _score(HOJE, 75),
        _score(HOJE - timedelta(days=1), None),
        _score(HOJE - timedelta(days=2), 75),
    ]
    assert regra.detectar(historico_desc) is None


def test_score_exatamente_70_nao_dispara() -> None:
    """Limiar é estritamente maior que 70."""
    regra = AlertBurnout()
    historico_desc = [_score(HOJE - timedelta(days=i), 70) for i in range(5)]
    assert regra.detectar(historico_desc) is None


def test_5_dias_consecutivos_acima_de_70_retorna_5() -> None:
    regra = AlertBurnout()
    historico_desc = [_score(HOJE - timedelta(days=i), 80) for i in range(5)]
    assert regra.detectar(historico_desc) == 5
