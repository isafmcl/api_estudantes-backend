"""Router de alertas (US14)."""

from fastapi import APIRouter, HTTPException, Query, status

from src.infrastructure.http.dependencies.providers import (
    AlertaServiceDep,
    UsuarioAtualDep,
)
from src.infrastructure.http.schemas.schemas import AlertaResponse

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get(
    "/",
    response_model=list[AlertaResponse],
    summary="Listar alertas do usuário (US14)",
)
def listar(
    usuario: UsuarioAtualDep,
    alerta_service: AlertaServiceDep,
    apenas_nao_lidos: bool = Query(False),
) -> list[AlertaResponse]:
    alertas = alerta_service.listar_alertas(usuario.id, apenas_nao_lidos=apenas_nao_lidos)
    return [
        AlertaResponse(
            id=a.id,
            tipo=a.tipo.value,
            titulo=a.titulo,
            mensagem=a.mensagem,
            lido=a.lido,
            criado_em=a.criado_em,
        )
        for a in alertas
    ]


@router.patch(
    "/{alerta_id}/lido",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar alerta como lido",
)
def marcar_lido(
    alerta_id: int,
    usuario: UsuarioAtualDep,
    alerta_service: AlertaServiceDep,
) -> None:
    if not alerta_service.marcar_como_lido(usuario.id, alerta_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado.")
