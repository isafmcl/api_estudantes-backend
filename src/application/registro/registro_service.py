"""RegistroService: orquestra os casos de uso de registros diários (DAS §4.3).

Aplica regras de negócio (LimiteDiário RN-002), persiste via repositórios
e publica eventos de domínio para outros bounded contexts reagirem.
"""

from src.application.dtos import (
    AlimentacaoDTO,
    AtividadeAcademicaDTO,
    AtividadeFisicaDTO,
    HumorDTO,
    InteracaoSocialDTO,
    SonoDTO,
)
from src.domain.business_rules.limite_diario import LimiteDiario
from src.domain.entities.registro_diario import (
    RegistroAlimentacao,
    RegistroAtividadeAcademica,
    RegistroAtividadeFisica,
    RegistroHumor,
    RegistroInteracaoSocial,
    RegistroSono,
)
from src.domain.events.event_bus import EventBus
from src.domain.events.eventos import RegistroSalvo
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


class RegistroService:
    """Caso de uso central de registros diários. Todas as deps injetadas (DIP)."""

    def __init__(
        self,
        humor_repo: IHumorRepo,
        sono_repo: ISonoRepo,
        atividade_academica_repo: IAtividadeAcademicaRepo,
        alimentacao_repo: IAlimentacaoRepo,
        atividade_fisica_repo: IAtividadeFisicaRepo,
        interacao_social_repo: IInteracaoSocialRepo,
        event_bus: EventBus,
    ) -> None:
        self._humor = humor_repo
        self._sono = sono_repo
        self._academica = atividade_academica_repo
        self._alimentacao = alimentacao_repo
        self._fisica = atividade_fisica_repo
        self._social = interacao_social_repo
        self._bus = event_bus

    # ── US03 Humor ───────────────────────────────────────────────────────────

    def registrar_humor(self, usuario_id: int, dto: HumorDTO) -> RegistroHumor:
        existente = self._humor.buscar(usuario_id, dto.data)
        LimiteDiario.garantir_unico(existente, "humor", dto.data)  # RN-002

        registro = RegistroHumor(
            usuario_id=usuario_id,
            data=dto.data,
            nivel=NivelHumor(dto.nivel),
            observacao=dto.observacao,
        )
        salvo = self._humor.salvar(registro)
        self._bus.publicar(RegistroSalvo(usuario_id=usuario_id, tipo_registro="humor", data=dto.data))
        return salvo

    # ── US05 Sono ────────────────────────────────────────────────────────────

    def registrar_sono(self, usuario_id: int, dto: SonoDTO) -> RegistroSono:
        existente = self._sono.buscar(usuario_id, dto.data)
        LimiteDiario.garantir_unico(existente, "sono", dto.data)

        registro = RegistroSono(
            usuario_id=usuario_id,
            data=dto.data,
            horas_dormidas=dto.horas_dormidas,
            qualidade=QualidadeSono(dto.qualidade),
            houve_interrupcoes=dto.houve_interrupcoes,
        )
        salvo = self._sono.salvar(registro)
        self._bus.publicar(RegistroSalvo(usuario_id=usuario_id, tipo_registro="sono", data=dto.data))
        return salvo

    # ── US04 Atividade Acadêmica (múltiplas por dia) ─────────────────────────

    def registrar_atividade_academica(
        self, usuario_id: int, dto: AtividadeAcademicaDTO
    ) -> RegistroAtividadeAcademica:
        registro = RegistroAtividadeAcademica(
            usuario_id=usuario_id,
            data=dto.data,
            descricao=dto.descricao,
            tempo_minutos=dto.tempo_minutos,
        )
        salvo = self._academica.salvar(registro)
        self._bus.publicar(
            RegistroSalvo(usuario_id=usuario_id, tipo_registro="atividade_academica", data=dto.data)
        )
        return salvo

    def remover_atividade_academica(self, usuario_id: int, registro_id: int) -> bool:
        return self._academica.remover(usuario_id, registro_id)

    # ── US06 Alimentação ─────────────────────────────────────────────────────

    def registrar_alimentacao(self, usuario_id: int, dto: AlimentacaoDTO) -> RegistroAlimentacao:
        existente = self._alimentacao.buscar(usuario_id, dto.data)
        LimiteDiario.garantir_unico(existente, "alimentacao", dto.data)

        registro = RegistroAlimentacao(
            usuario_id=usuario_id,
            data=dto.data,
            qualidade=QualidadeAlimentacao(dto.qualidade),
        )
        salvo = self._alimentacao.salvar(registro)
        self._bus.publicar(RegistroSalvo(usuario_id=usuario_id, tipo_registro="alimentacao", data=dto.data))
        return salvo

    # ── US07 Atividade Física ────────────────────────────────────────────────

    def registrar_atividade_fisica(
        self, usuario_id: int, dto: AtividadeFisicaDTO
    ) -> RegistroAtividadeFisica:
        existente = self._fisica.buscar(usuario_id, dto.data)
        LimiteDiario.garantir_unico(existente, "atividade_fisica", dto.data)

        registro = RegistroAtividadeFisica(
            usuario_id=usuario_id,
            data=dto.data,
            nivel=NivelAtividadeFisica(dto.nivel),
        )
        salvo = self._fisica.salvar(registro)
        self._bus.publicar(
            RegistroSalvo(usuario_id=usuario_id, tipo_registro="atividade_fisica", data=dto.data)
        )
        return salvo

    # ── US08 Interação Social ────────────────────────────────────────────────

    def registrar_interacao_social(
        self, usuario_id: int, dto: InteracaoSocialDTO
    ) -> RegistroInteracaoSocial:
        existente = self._social.buscar(usuario_id, dto.data)
        LimiteDiario.garantir_unico(existente, "interacao_social", dto.data)

        registro = RegistroInteracaoSocial(
            usuario_id=usuario_id,
            data=dto.data,
            qualidade=QualidadeInteracaoSocial(dto.qualidade),
            teve_interacao=dto.teve_interacao,
        )
        salvo = self._social.salvar(registro)
        self._bus.publicar(
            RegistroSalvo(usuario_id=usuario_id, tipo_registro="interacao_social", data=dto.data)
        )
        return salvo
