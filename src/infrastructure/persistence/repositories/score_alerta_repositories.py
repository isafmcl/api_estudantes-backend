"""Implementações dos repositórios de Score e Alerta."""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.score_estresse import Alerta, DetalheSubScore, ScoreEstresse
from src.domain.interfaces.i_alerta import IAlertaRepo
from src.domain.interfaces.i_score_repo import IScoreRepo
from src.domain.value_objects.enums import NivelEstresse, TipoAlerta
from src.domain.value_objects.periodo_datas import PeriodoDatas
from src.infrastructure.persistence.models.orm_models import AlertaModel, ScoreEstresseModel


class ScoreRepository(IScoreRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[ScoreEstresse]:
        m = (
            self._session.query(ScoreEstresseModel)
            .filter(ScoreEstresseModel.usuario_id == usuario_id, ScoreEstresseModel.data == dia)
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(self, usuario_id: int, periodo: PeriodoDatas) -> list[ScoreEstresse]:
        results = (
            self._session.query(ScoreEstresseModel)
            .filter(
                ScoreEstresseModel.usuario_id == usuario_id,
                ScoreEstresseModel.data >= periodo.inicio,
                ScoreEstresseModel.data <= periodo.fim,
            )
            .order_by(ScoreEstresseModel.data.asc())
            .all()
        )
        return [self._to_entity(m) for m in results]

    def salvar_ou_atualizar(self, score: ScoreEstresse) -> ScoreEstresse:
        existente = (
            self._session.query(ScoreEstresseModel)
            .filter(
                ScoreEstresseModel.usuario_id == score.usuario_id,
                ScoreEstresseModel.data == score.data,
            )
            .first()
        )
        if existente:
            existente.score = score.score
            existente.nivel = score.nivel.value
            existente.percentual_dados = score.percentual_dados_registrados
            self._session.commit()
            self._session.refresh(existente)
            return self._to_entity(existente, detalhes=score.detalhes)

        m = ScoreEstresseModel(
            usuario_id=score.usuario_id,
            data=score.data,
            score=score.score,
            nivel=score.nivel.value,
            percentual_dados=score.percentual_dados_registrados,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m, detalhes=score.detalhes)

    @staticmethod
    def _to_entity(
        m: ScoreEstresseModel, detalhes: Optional[dict[str, DetalheSubScore]] = None
    ) -> ScoreEstresse:
        return ScoreEstresse(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            score=m.score,
            nivel=NivelEstresse(m.nivel),
            detalhes=detalhes or {},
            percentual_dados_registrados=m.percentual_dados,
            criado_em=m.criado_em,
        )


class AlertaRepository(IAlertaRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def listar_do_usuario(self, usuario_id: int, apenas_nao_lidos: bool = False) -> list[Alerta]:
        query = self._session.query(AlertaModel).filter(AlertaModel.usuario_id == usuario_id)
        if apenas_nao_lidos:
            query = query.filter(AlertaModel.lido == False)  # noqa: E712
        return [self._to_entity(m) for m in query.order_by(AlertaModel.criado_em.desc()).all()]

    def existe_recente(self, usuario_id: int, tipo: str, horas: int = 24) -> bool:
        limite = datetime.utcnow() - timedelta(hours=horas)
        return (
            self._session.query(AlertaModel)
            .filter(
                AlertaModel.usuario_id == usuario_id,
                AlertaModel.tipo == tipo,
                AlertaModel.criado_em >= limite,
            )
            .first()
            is not None
        )

    def salvar(self, alerta: Alerta) -> Alerta:
        m = AlertaModel(
            usuario_id=alerta.usuario_id,
            tipo=alerta.tipo.value,
            titulo=alerta.titulo,
            mensagem=alerta.mensagem,
            lido=alerta.lido,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    def marcar_como_lido(self, usuario_id: int, alerta_id: int) -> bool:
        m = (
            self._session.query(AlertaModel)
            .filter(AlertaModel.id == alerta_id, AlertaModel.usuario_id == usuario_id)
            .first()
        )
        if not m:
            return False
        m.lido = True
        self._session.commit()
        return True

    @staticmethod
    def _to_entity(m: AlertaModel) -> Alerta:
        return Alerta(
            id=m.id,
            usuario_id=m.usuario_id,
            tipo=TipoAlerta(m.tipo),
            titulo=m.titulo,
            mensagem=m.mensagem,
            lido=m.lido,
            criado_em=m.criado_em,
        )
