"""AlertaService: emissão de alertas (DAS §4.3 notif.app).

Reage a eventos ScoreAtualizado, avalia regras de negócio (AlertBurnout RN-003)
e emite alertas se aplicável.
"""

from typing import Optional

from src.domain.business_rules.alert_burnout import AlertBurnout
from src.domain.entities.score_estresse import Alerta
from src.domain.events.event_bus import EventBus
from src.domain.events.eventos import AlertaGerado, BurnoutDetectado, ScoreAtualizado
from src.domain.interfaces.i_alerta import IAlertaRepo, IAlertaService
from src.domain.interfaces.i_score_repo import IScoreRepo
from src.domain.value_objects.enums import TipoAlerta
from src.domain.value_objects.periodo_datas import PeriodoDatas


class AlertaService(IAlertaService):
    """Avalia regras de alerta e persiste novos alertas (RN-003, US14)."""

    def __init__(
        self,
        alerta_repo: IAlertaRepo,
        score_repo: IScoreRepo,
        regra_burnout: AlertBurnout,
        event_bus: EventBus,
    ) -> None:
        self._repo = alerta_repo
        self._scores = score_repo
        self._burnout = regra_burnout
        self._bus = event_bus

    def avaliar_e_emitir(self, usuario_id: int) -> Optional[Alerta]:
        """RN-003: verifica se há 3+ dias consecutivos com score > 70."""
        periodo = PeriodoDatas.ultimos_n_dias(7)
        scores = self._scores.listar(usuario_id, periodo)
        # Ordem decrescente: mais recente primeiro
        scores_desc = sorted(scores, key=lambda s: s.data, reverse=True)

        dias = self._burnout.detectar(scores_desc)
        if dias is None:
            return None

        # Evita spam: só gera novo alerta se não houver um recente
        if self._repo.existe_recente(usuario_id, TipoAlerta.BURNOUT.value, horas=24):
            return None

        alerta = Alerta(
            usuario_id=usuario_id,
            tipo=TipoAlerta.BURNOUT,
            titulo="Padrão de estresse elevado detectado",
            mensagem=(
                f"Seu nível de estresse está acima de 70 há {dias} dias consecutivos. "
                "Considere pausas, sono regular e procurar apoio se necessário."
            ),
        )
        salvo = self._repo.salvar(alerta)
        self._bus.publicar(BurnoutDetectado(usuario_id=usuario_id, dias_consecutivos=dias))
        self._bus.publicar(AlertaGerado(usuario_id=usuario_id, tipo=alerta.tipo.value, titulo=alerta.titulo))
        return salvo

    def listar_alertas(self, usuario_id: int, apenas_nao_lidos: bool = False) -> list[Alerta]:
        return self._repo.listar_do_usuario(usuario_id, apenas_nao_lidos=apenas_nao_lidos)

    def marcar_como_lido(self, usuario_id: int, alerta_id: int) -> bool:
        return self._repo.marcar_como_lido(usuario_id, alerta_id)


# ───── Handler de evento: dispara avaliação após cada ScoreAtualizado ───────


def criar_handler_alerta(alerta_service: AlertaService):
    """Factory que retorna handler para o EventBus.

    Mantém o service desacoplado do EventBus diretamente.
    """

    def handler(evento: ScoreAtualizado) -> None:
        if evento.score is not None and evento.score > 70:
            alerta_service.avaliar_e_emitir(evento.usuario_id)

    return handler
