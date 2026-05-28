"""Router dos registros diários (US03–US08)."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos import (
    AlimentacaoDTO,
    AtividadeAcademicaDTO,
    AtividadeFisicaDTO,
    HumorDTO,
    InteracaoSocialDTO,
    SonoDTO,
)
from src.application.estresse.estresse_service import EstresseService
from src.domain.business_rules.limite_diario import LimiteDiarioExcedido
from src.infrastructure.http.dependencies.providers import (
    EstresseServiceDep,
    RegistroServiceDep,
    UsuarioAtualDep,
)
from src.infrastructure.http.schemas.schemas import (
    AlimentacaoRequest,
    AlimentacaoResponse,
    AtividadeAcademicaRequest,
    AtividadeAcademicaResponse,
    AtividadeFisicaRequest,
    AtividadeFisicaResponse,
    HumorRequest,
    HumorResponse,
    InteracaoSocialRequest,
    InteracaoSocialResponse,
    SonoRequest,
    SonoResponse,
)

router = APIRouter(prefix="/registros", tags=["Registros Diários"])


def _recalcular_score(
    estresse: EstresseService, usuario_id: int, dia: date
) -> None:
    """US09-CA3: recalcular score sempre que novos dados forem registrados."""
    try:
        estresse.calcular_e_persistir_do_dia(usuario_id, dia)
    except Exception as exc:  # noqa: BLE001
        # Falha em recálculo não deve quebrar o registro.
        print(f"[WARN] Falha ao recalcular score: {exc}")


# ───── Humor (US03) ─────────────────────────────────────────────────────────


@router.post(
    "/humor",
    response_model=HumorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar humor do dia (US03)",
)
def criar_humor(
    req: HumorRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> HumorResponse:
    try:
        salvo = registro.registrar_humor(
            usuario.id,
            HumorDTO(data=req.data, nivel=req.nivel, observacao=req.observacao),
        )
    except LimiteDiarioExcedido as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    _recalcular_score(estresse, usuario.id, req.data)
    return HumorResponse(
        id=salvo.id,
        data=salvo.data,
        nivel=salvo.nivel.value,
        observacao=salvo.observacao,
    )


# ───── Sono (US05) ──────────────────────────────────────────────────────────


@router.post(
    "/sono",
    response_model=SonoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar sono do dia (US05)",
)
def criar_sono(
    req: SonoRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> SonoResponse:
    try:
        salvo = registro.registrar_sono(
            usuario.id,
            SonoDTO(
                data=req.data,
                horas_dormidas=req.horas_dormidas,
                qualidade=req.qualidade,
                houve_interrupcoes=req.houve_interrupcoes,
            ),
        )
    except LimiteDiarioExcedido as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    _recalcular_score(estresse, usuario.id, req.data)
    return SonoResponse(
        id=salvo.id,
        data=salvo.data,
        horas_dormidas=salvo.horas_dormidas,
        qualidade=salvo.qualidade.value,
        houve_interrupcoes=salvo.houve_interrupcoes,
    )


# ───── Atividade Acadêmica (US04) ───────────────────────────────────────────


@router.post(
    "/atividades-academicas",
    response_model=AtividadeAcademicaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar atividade acadêmica (US04)",
)
def criar_atividade_academica(
    req: AtividadeAcademicaRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> AtividadeAcademicaResponse:
    salvo = registro.registrar_atividade_academica(
        usuario.id,
        AtividadeAcademicaDTO(
            data=req.data, descricao=req.descricao, tempo_minutos=req.tempo_minutos
        ),
    )
    _recalcular_score(estresse, usuario.id, req.data)
    return AtividadeAcademicaResponse(
        id=salvo.id,
        data=salvo.data,
        descricao=salvo.descricao,
        tempo_minutos=salvo.tempo_minutos,
    )


@router.delete(
    "/atividades-academicas/{registro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover atividade acadêmica",
)
def remover_atividade_academica(
    registro_id: int,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
) -> None:
    if not registro.remover_atividade_academica(usuario.id, registro_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")


# ───── Alimentação (US06) ───────────────────────────────────────────────────


@router.post(
    "/alimentacao",
    response_model=AlimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar alimentação (US06)",
)
def criar_alimentacao(
    req: AlimentacaoRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> AlimentacaoResponse:
    try:
        salvo = registro.registrar_alimentacao(
            usuario.id, AlimentacaoDTO(data=req.data, qualidade=req.qualidade)
        )
    except LimiteDiarioExcedido as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    _recalcular_score(estresse, usuario.id, req.data)
    return AlimentacaoResponse(id=salvo.id, data=salvo.data, qualidade=salvo.qualidade.value)


# ───── Atividade Física (US07) ──────────────────────────────────────────────


@router.post(
    "/atividade-fisica",
    response_model=AtividadeFisicaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar atividade física (US07)",
)
def criar_atividade_fisica(
    req: AtividadeFisicaRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> AtividadeFisicaResponse:
    try:
        salvo = registro.registrar_atividade_fisica(
            usuario.id, AtividadeFisicaDTO(data=req.data, nivel=req.nivel)
        )
    except LimiteDiarioExcedido as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    _recalcular_score(estresse, usuario.id, req.data)
    return AtividadeFisicaResponse(id=salvo.id, data=salvo.data, nivel=salvo.nivel.value)


# ───── Interação Social (US08) ──────────────────────────────────────────────


@router.post(
    "/interacao-social",
    response_model=InteracaoSocialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar interação social (US08)",
)
def criar_interacao_social(
    req: InteracaoSocialRequest,
    usuario: UsuarioAtualDep,
    registro: RegistroServiceDep,
    estresse: EstresseServiceDep,
) -> InteracaoSocialResponse:
    try:
        salvo = registro.registrar_interacao_social(
            usuario.id,
            InteracaoSocialDTO(
                data=req.data, qualidade=req.qualidade, teve_interacao=req.teve_interacao
            ),
        )
    except LimiteDiarioExcedido as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    _recalcular_score(estresse, usuario.id, req.data)
    return InteracaoSocialResponse(
        id=salvo.id,
        data=salvo.data,
        qualidade=salvo.qualidade.value,
        teve_interacao=salvo.teve_interacao,
    )
