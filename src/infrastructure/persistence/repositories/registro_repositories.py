"""Implementações SQLAlchemy de todos os repositórios de registros diários.

Cada um implementa sua port respectiva e faz tradução ORM ↔ Entity.
"""

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.registro_diario import (
    RegistroAlimentacao,
    RegistroAtividadeAcademica,
    RegistroAtividadeFisica,
    RegistroHumor,
    RegistroInteracaoSocial,
    RegistroSono,
)
from src.domain.interfaces.i_registro_repo import (
    IAlimentacaoRepo,
    IAtividadeAcademicaRepo,
    IAtividadeFisicaRepo,
    IHumorRepo,
    IInteracaoSocialRepo,
    ISonoRepo,
)
from src.domain.value_objects.enums import (
    NivelAtividadeFisica,
    NivelHumor,
    QualidadeAlimentacao,
    QualidadeInteracaoSocial,
    QualidadeSono,
)
from src.domain.value_objects.periodo_datas import PeriodoDatas
from src.infrastructure.persistence.models.orm_models import (
    AlimentacaoModel,
    AtividadeAcademicaModel,
    AtividadeFisicaModel,
    HumorModel,
    InteracaoSocialModel,
    SonoModel,
)


# ───── Humor ────────────────────────────────────────────────────────────────


class HumorRepository(IHumorRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroHumor]:
        m = (
            self._session.query(HumorModel)
            .filter(HumorModel.usuario_id == usuario_id, HumorModel.data == dia)
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroHumor]:
        query = self._session.query(HumorModel).filter(HumorModel.usuario_id == usuario_id)
        if periodo:
            query = query.filter(HumorModel.data >= periodo.inicio, HumorModel.data <= periodo.fim)
        return [self._to_entity(m) for m in query.order_by(HumorModel.data.desc()).all()]

    def salvar(self, registro: RegistroHumor) -> RegistroHumor:
        m = HumorModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            nivel=registro.nivel.value,
            observacao=registro.observacao,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    @staticmethod
    def _to_entity(m: HumorModel) -> RegistroHumor:
        return RegistroHumor(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            nivel=NivelHumor(m.nivel),
            observacao=m.observacao,
        )


# ───── Sono ─────────────────────────────────────────────────────────────────


class SonoRepository(ISonoRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroSono]:
        m = (
            self._session.query(SonoModel)
            .filter(SonoModel.usuario_id == usuario_id, SonoModel.data == dia)
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroSono]:
        query = self._session.query(SonoModel).filter(SonoModel.usuario_id == usuario_id)
        if periodo:
            query = query.filter(SonoModel.data >= periodo.inicio, SonoModel.data <= periodo.fim)
        return [self._to_entity(m) for m in query.order_by(SonoModel.data.desc()).all()]

    def salvar(self, registro: RegistroSono) -> RegistroSono:
        m = SonoModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            horas_dormidas=registro.horas_dormidas,
            qualidade=registro.qualidade.value,
            houve_interrupcoes=registro.houve_interrupcoes,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    @staticmethod
    def _to_entity(m: SonoModel) -> RegistroSono:
        return RegistroSono(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            horas_dormidas=m.horas_dormidas,
            qualidade=QualidadeSono(m.qualidade),
            houve_interrupcoes=m.houve_interrupcoes,
        )


# ───── Atividade Acadêmica ──────────────────────────────────────────────────


class AtividadeAcademicaRepository(IAtividadeAcademicaRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar_por_id(self, usuario_id: int, registro_id: int) -> Optional[RegistroAtividadeAcademica]:
        m = (
            self._session.query(AtividadeAcademicaModel)
            .filter(
                AtividadeAcademicaModel.id == registro_id,
                AtividadeAcademicaModel.usuario_id == usuario_id,
            )
            .first()
        )
        return self._to_entity(m) if m else None

    def listar_do_dia(self, usuario_id: int, dia: date) -> list[RegistroAtividadeAcademica]:
        results = (
            self._session.query(AtividadeAcademicaModel)
            .filter(
                AtividadeAcademicaModel.usuario_id == usuario_id,
                AtividadeAcademicaModel.data == dia,
            )
            .all()
        )
        return [self._to_entity(m) for m in results]

    def listar(
        self, usuario_id: int, periodo: Optional[PeriodoDatas] = None
    ) -> list[RegistroAtividadeAcademica]:
        query = self._session.query(AtividadeAcademicaModel).filter(
            AtividadeAcademicaModel.usuario_id == usuario_id
        )
        if periodo:
            query = query.filter(
                AtividadeAcademicaModel.data >= periodo.inicio,
                AtividadeAcademicaModel.data <= periodo.fim,
            )
        return [
            self._to_entity(m)
            for m in query.order_by(AtividadeAcademicaModel.data.desc()).all()
        ]

    def salvar(self, registro: RegistroAtividadeAcademica) -> RegistroAtividadeAcademica:
        m = AtividadeAcademicaModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            descricao=registro.descricao,
            tempo_minutos=registro.tempo_minutos,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    def remover(self, usuario_id: int, registro_id: int) -> bool:
        m = (
            self._session.query(AtividadeAcademicaModel)
            .filter(
                AtividadeAcademicaModel.id == registro_id,
                AtividadeAcademicaModel.usuario_id == usuario_id,
            )
            .first()
        )
        if not m:
            return False
        self._session.delete(m)
        self._session.commit()
        return True

    @staticmethod
    def _to_entity(m: AtividadeAcademicaModel) -> RegistroAtividadeAcademica:
        return RegistroAtividadeAcademica(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            descricao=m.descricao,
            tempo_minutos=m.tempo_minutos,
        )


# ───── Alimentação ──────────────────────────────────────────────────────────


class AlimentacaoRepository(IAlimentacaoRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroAlimentacao]:
        m = (
            self._session.query(AlimentacaoModel)
            .filter(AlimentacaoModel.usuario_id == usuario_id, AlimentacaoModel.data == dia)
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(self, usuario_id: int, periodo: Optional[PeriodoDatas] = None) -> list[RegistroAlimentacao]:
        query = self._session.query(AlimentacaoModel).filter(AlimentacaoModel.usuario_id == usuario_id)
        if periodo:
            query = query.filter(
                AlimentacaoModel.data >= periodo.inicio, AlimentacaoModel.data <= periodo.fim
            )
        return [self._to_entity(m) for m in query.order_by(AlimentacaoModel.data.desc()).all()]

    def salvar(self, registro: RegistroAlimentacao) -> RegistroAlimentacao:
        m = AlimentacaoModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            qualidade=registro.qualidade.value,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    @staticmethod
    def _to_entity(m: AlimentacaoModel) -> RegistroAlimentacao:
        return RegistroAlimentacao(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            qualidade=QualidadeAlimentacao(m.qualidade),
        )


# ───── Atividade Física ─────────────────────────────────────────────────────


class AtividadeFisicaRepository(IAtividadeFisicaRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroAtividadeFisica]:
        m = (
            self._session.query(AtividadeFisicaModel)
            .filter(
                AtividadeFisicaModel.usuario_id == usuario_id, AtividadeFisicaModel.data == dia
            )
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(
        self, usuario_id: int, periodo: Optional[PeriodoDatas] = None
    ) -> list[RegistroAtividadeFisica]:
        query = self._session.query(AtividadeFisicaModel).filter(
            AtividadeFisicaModel.usuario_id == usuario_id
        )
        if periodo:
            query = query.filter(
                AtividadeFisicaModel.data >= periodo.inicio,
                AtividadeFisicaModel.data <= periodo.fim,
            )
        return [self._to_entity(m) for m in query.order_by(AtividadeFisicaModel.data.desc()).all()]

    def salvar(self, registro: RegistroAtividadeFisica) -> RegistroAtividadeFisica:
        m = AtividadeFisicaModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            nivel=registro.nivel.value,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    @staticmethod
    def _to_entity(m: AtividadeFisicaModel) -> RegistroAtividadeFisica:
        return RegistroAtividadeFisica(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            nivel=NivelAtividadeFisica(m.nivel),
        )


# ───── Interação Social ─────────────────────────────────────────────────────


class InteracaoSocialRepository(IInteracaoSocialRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, usuario_id: int, dia: date) -> Optional[RegistroInteracaoSocial]:
        m = (
            self._session.query(InteracaoSocialModel)
            .filter(
                InteracaoSocialModel.usuario_id == usuario_id, InteracaoSocialModel.data == dia
            )
            .first()
        )
        return self._to_entity(m) if m else None

    def listar(
        self, usuario_id: int, periodo: Optional[PeriodoDatas] = None
    ) -> list[RegistroInteracaoSocial]:
        query = self._session.query(InteracaoSocialModel).filter(
            InteracaoSocialModel.usuario_id == usuario_id
        )
        if periodo:
            query = query.filter(
                InteracaoSocialModel.data >= periodo.inicio,
                InteracaoSocialModel.data <= periodo.fim,
            )
        return [self._to_entity(m) for m in query.order_by(InteracaoSocialModel.data.desc()).all()]

    def salvar(self, registro: RegistroInteracaoSocial) -> RegistroInteracaoSocial:
        m = InteracaoSocialModel(
            usuario_id=registro.usuario_id,
            data=registro.data,
            qualidade=registro.qualidade.value,
            teve_interacao=registro.teve_interacao,
        )
        self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return self._to_entity(m)

    @staticmethod
    def _to_entity(m: InteracaoSocialModel) -> RegistroInteracaoSocial:
        return RegistroInteracaoSocial(
            id=m.id,
            usuario_id=m.usuario_id,
            data=m.data,
            qualidade=QualidadeInteracaoSocial(m.qualidade),
            teve_interacao=m.teve_interacao,
        )
