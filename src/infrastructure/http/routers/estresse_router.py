"""Router de score de estresse e histórico (US09, US13, US14)."""

from datetime import date as date_type

from fastapi import APIRouter, Query

from src.domain.business_rules.alert_burnout import AlertBurnout
from src.infrastructure.http.dependencies.providers import (
    EstresseServiceDep,
    UsuarioAtualDep,
)
from src.infrastructure.http.schemas.schemas import (
    AlertaBurnoutInfo,
    DetalheSubScoreSchema,
    HistoricoItemResponse,
    HistoricoResponse,
    ScoreResponse,
)

router = APIRouter(prefix="/estresse", tags=["Score de Estresse"])


# ───── Mapeamento de níveis para UI (cor/emoji) ─────────────────────────────

_CORES = {
    "baixo": "#43a047",
    "moderado": "#fb8c00",
    "elevado": "#ff5722",
    "critico": "#e53935",
    "indefinido": "#9e9e9e",
}

_EMOJIS = {
    "baixo": "😊",
    "moderado": "😐",
    "elevado": "😟",
    "critico": "🚨",
    "indefinido": "❓",
}


@router.get(
    "/score",
    response_model=ScoreResponse,
    summary="Score de estresse de um dia (US09)",
)
def score_do_dia(
    usuario: UsuarioAtualDep,
    estresse: EstresseServiceDep,
    data: date_type | None = Query(None, description="Data do score (default: hoje)"),
) -> ScoreResponse:
    dia = data or date_type.today()
    resultado = estresse.calcular_do_dia(usuario.id, dia)

    nivel = resultado.nivel.value
    return ScoreResponse(
        data=dia,
        score=resultado.score,
        nivel=nivel,
        detalhes={
            chave: DetalheSubScoreSchema(sub_score=det.sub_score, peso=det.peso)
            for chave, det in resultado.detalhes.items()
        },
        percentual_dados_registrados=resultado.percentual_dados_registrados,
        cor_indicativa=_CORES.get(nivel, _CORES["indefinido"]),
        emoji=_EMOJIS.get(nivel, _EMOJIS["indefinido"]),
    )


@router.get(
    "/historico",
    response_model=HistoricoResponse,
    summary="Histórico de scores e alerta de burnout (US13, US14, RN-003)",
)
def historico_score(
    usuario: UsuarioAtualDep,
    estresse: EstresseServiceDep,
    dias: int = Query(7, ge=1, le=90),
) -> HistoricoResponse:
    historico = estresse.historico(usuario.id, dias)
    items = [
        HistoricoItemResponse(data=s.data, score=s.score, nivel=s.nivel.value) for s in historico
    ]

    # RN-003: avaliar alerta de burnout sobre o histórico calculado
    regra = AlertBurnout()
    historico_desc = sorted(historico, key=lambda s: s.data, reverse=True)
    dias_consecutivos = regra.detectar(historico_desc)

    if dias_consecutivos is not None:
        alerta = AlertaBurnoutInfo(
            alerta=True,
            dias_consecutivos=dias_consecutivos,
            mensagem=(
                f"⚠️ Seu nível de estresse está acima de 70 há {dias_consecutivos} dias "
                "consecutivos. Considere pausas e procure apoio se necessário."
            ),
        )
    else:
        alerta = AlertaBurnoutInfo(alerta=False)

    return HistoricoResponse(historico=items, alerta_burnout=alerta)
