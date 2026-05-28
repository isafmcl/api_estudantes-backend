"""Container de Injeção de Dependências (Composition Root).

Aqui — e SOMENTE aqui — instâncias concretas são amarradas às interfaces.
O resto do código depende apenas de abstrações.
"""

from sqlalchemy.orm import Session

from src.application.auth.auth_service import AuthService
from src.application.estresse.alerta_service import AlertaService, criar_handler_alerta
from src.application.estresse.estresse_service import EstresseService
from src.application.registro.registro_service import RegistroService
from src.config.settings import Settings
from src.domain.business_rules.alert_burnout import AlertBurnout
from src.domain.business_rules.score_engine import ScoreEngine
from src.domain.events.event_bus import EventBus
from src.domain.events.eventos import ScoreAtualizado
from src.infrastructure.persistence.repositories.registro_repositories import (
    AlimentacaoRepository,
    AtividadeAcademicaRepository,
    AtividadeFisicaRepository,
    HumorRepository,
    InteracaoSocialRepository,
    SonoRepository,
)
from src.infrastructure.persistence.repositories.score_alerta_repositories import (
    AlertaRepository,
    ScoreRepository,
)
from src.infrastructure.persistence.repositories.usuario_repository import UsuarioRepository
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.infrastructure.security.token_service import JwtTokenService


class Container:
    """Composition root: amarra todas as dependências da aplicação."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        # ── Dependências singleton (sem estado por requisição) ──
        self.hasher = BcryptPasswordHasher()
        self.token_service = JwtTokenService(
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            expire_minutes=settings.jwt_expire_minutes,
        )
        self.score_engine = ScoreEngine()
        self.regra_burnout = AlertBurnout()
        self.event_bus = EventBus()

    def construir_auth_service(self, session: Session) -> AuthService:
        return AuthService(
            usuario_repo=UsuarioRepository(session),
            hasher=self.hasher,
            token_service=self.token_service,
        )

    def construir_registro_service(self, session: Session) -> RegistroService:
        return RegistroService(
            humor_repo=HumorRepository(session),
            sono_repo=SonoRepository(session),
            atividade_academica_repo=AtividadeAcademicaRepository(session),
            alimentacao_repo=AlimentacaoRepository(session),
            atividade_fisica_repo=AtividadeFisicaRepository(session),
            interacao_social_repo=InteracaoSocialRepository(session),
            event_bus=self.event_bus,
        )

    def construir_estresse_service(self, session: Session) -> EstresseService:
        return EstresseService(
            humor_repo=HumorRepository(session),
            sono_repo=SonoRepository(session),
            academica_repo=AtividadeAcademicaRepository(session),
            alimentacao_repo=AlimentacaoRepository(session),
            fisica_repo=AtividadeFisicaRepository(session),
            social_repo=InteracaoSocialRepository(session),
            score_repo=ScoreRepository(session),
            engine=self.score_engine,
            event_bus=self.event_bus,
        )

    def construir_alerta_service(self, session: Session) -> AlertaService:
        return AlertaService(
            alerta_repo=AlertaRepository(session),
            score_repo=ScoreRepository(session),
            regra_burnout=self.regra_burnout,
            event_bus=self.event_bus,
        )

    def registrar_handlers_de_evento(self, session_factory) -> None:
        """Inscreve handlers no event bus.

        Como o handler precisa de sessão por chamada, recebe a factory.
        """

        def on_score_atualizado(evento: ScoreAtualizado) -> None:
            if evento.score is None or evento.score <= 70:
                return
            with session_factory() as session:
                alerta_service = self.construir_alerta_service(session)
                handler = criar_handler_alerta(alerta_service)
                handler(evento)

        self.event_bus.inscrever(ScoreAtualizado, on_score_atualizado)
