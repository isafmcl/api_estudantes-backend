"""EstresseService: orquestra cálculo do score (DAS §4.3 estresse.app).

Responsável por:
  - Buscar todos os registros do dia via repositórios.
  - Invocar o ScoreEngine (regra de negócio pura).
  - Persistir o score calculado.
  - Publicar evento ScoreAtualizado.
"""

from datetime import date

from src.domain.business_rules.score_engine import DadosDoDia, ScoreEngine
from src.domain.entities.score_estresse import ScoreEstresse
from src.domain.events.event_bus import EventBus
from src.domain.events.eventos import ScoreAtualizado
from src.domain.interfaces.i_registro_repo import (
    IAlimentacaoRepo,
    IAtividadeAcademicaRepo,
    IAtividadeFisicaRepo,
    IHumorRepo,
    IInteracaoSocialRepo,
    ISonoRepo,
)
from src.domain.interfaces.i_score_repo import IScoreRepo
from src.domain.value_objects.periodo_datas import PeriodoDatas


class EstresseService:
    """Caso de uso de cálculo e consulta de score de estresse (US09, US13)."""

    def __init__(
        self,
        humor_repo: IHumorRepo,
        sono_repo: ISonoRepo,
        academica_repo: IAtividadeAcademicaRepo,
        alimentacao_repo: IAlimentacaoRepo,
        fisica_repo: IAtividadeFisicaRepo,
        social_repo: IInteracaoSocialRepo,
        score_repo: IScoreRepo,
        engine: ScoreEngine,
        event_bus: EventBus,
    ) -> None:
        self._humor = humor_repo
        self._sono = sono_repo
        self._academica = academica_repo
        self._alimentacao = alimentacao_repo
        self._fisica = fisica_repo
        self._social = social_repo
        self._score_repo = score_repo
        self._engine = engine
        self._bus = event_bus

    def calcular_e_persistir_do_dia(self, usuario_id: int, dia: date) -> ScoreEstresse:
        """US09 + US09-CA3: recalcula score sempre que novos dados são registrados."""
        dados = self._coletar_dados_do_dia(usuario_id, dia)
        score = self._engine.calcular(usuario_id, dia, dados)
        persistido = self._score_repo.salvar_ou_atualizar(score)
        self._bus.publicar(
            ScoreAtualizado(
                usuario_id=usuario_id,
                data=dia,
                score=persistido.score,
                nivel=persistido.nivel.value,
            )
        )
        return persistido

    def calcular_do_dia(self, usuario_id: int, dia: date) -> ScoreEstresse:
        """Cálculo on-demand sem persistir (consulta direta)."""
        dados = self._coletar_dados_do_dia(usuario_id, dia)
        return self._engine.calcular(usuario_id, dia, dados)

    def historico(self, usuario_id: int, dias: int) -> list[ScoreEstresse]:
        """Retorna o histórico de scores dos últimos N dias (US13, US16).

        Para cada dia do período, calcula on-demand a partir dos registros.
        Evita N×6 queries usando batch loading (otimização principal vs versão antiga).
        """
        periodo = PeriodoDatas.ultimos_n_dias(dias)

        # Carrega todos os registros do período em uma query por tipo (6 queries totais).
        humores = self._humor.listar(usuario_id, periodo)
        sonos = self._sono.listar(usuario_id, periodo)
        academicas = self._academica.listar(usuario_id, periodo)
        alimentacoes = self._alimentacao.listar(usuario_id, periodo)
        fisicas = self._fisica.listar(usuario_id, periodo)
        sociais = self._social.listar(usuario_id, periodo)

        # Indexa por data para acesso O(1)
        humor_por_data = {r.data: r for r in humores}
        sono_por_data = {r.data: r for r in sonos}
        alimentacao_por_data = {r.data: r for r in alimentacoes}
        fisica_por_data = {r.data: r for r in fisicas}
        social_por_data = {r.data: r for r in sociais}

        academicas_por_data: dict[date, list] = {}
        for r in academicas:
            academicas_por_data.setdefault(r.data, []).append(r)

        # Calcula score para cada dia do período
        resultado: list[ScoreEstresse] = []
        from datetime import timedelta

        dia = periodo.inicio
        while dia <= periodo.fim:
            dados = DadosDoDia(
                humor=humor_por_data.get(dia),
                sono=sono_por_data.get(dia),
                atividades_academicas=academicas_por_data.get(dia, []),
                alimentacao=alimentacao_por_data.get(dia),
                atividade_fisica=fisica_por_data.get(dia),
                interacao_social=social_por_data.get(dia),
            )
            resultado.append(self._engine.calcular(usuario_id, dia, dados))
            dia += timedelta(days=1)

        return resultado

    # ───── helpers privados ──────────────────────────────────────────────────

    def _coletar_dados_do_dia(self, usuario_id: int, dia: date) -> DadosDoDia:
        return DadosDoDia(
            humor=self._humor.buscar(usuario_id, dia),
            sono=self._sono.buscar(usuario_id, dia),
            atividades_academicas=self._academica.listar_do_dia(usuario_id, dia),
            alimentacao=self._alimentacao.buscar(usuario_id, dia),
            atividade_fisica=self._fisica.buscar(usuario_id, dia),
            interacao_social=self._social.buscar(usuario_id, dia),
        )
