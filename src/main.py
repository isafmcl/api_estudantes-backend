"""Bootstrap da aplicação FastAPI (DAS §4.3 Apresentação → API REST)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings
from src.infrastructure.http.dependencies import providers
from src.infrastructure.http.dependencies.container import Container
from src.infrastructure.http.routers import (
    alerta_router,
    auth_router,
    estresse_router,
    registro_router,
)
from src.infrastructure.persistence.database import Base, criar_engine_e_session


def criar_app(settings: Settings | None = None) -> FastAPI:
    """Application factory. Permite testes com settings alternativas."""
    settings = settings or Settings.from_env()

    # ── Infraestrutura ──
    engine, SessionLocal = criar_engine_e_session(settings)

    # Importa os models antes do create_all para registrar todas as tabelas
    from src.infrastructure.persistence.models import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ── Composition Root ──
    container = Container(settings)
    container.registrar_handlers_de_evento(SessionLocal)
    providers.configurar(container, SessionLocal)

    # ── FastAPI ──
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=(
            "MindTrack — API REST para monitoramento de burnout acadêmico.\n\n"
            "Arquitetura limpa em 3 camadas (Apresentação / Aplicação / Domínio) "
            "conforme DAS §4.3."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["Sistema"])
    def root() -> dict:
        return {"app": "MindTrack API", "version": settings.api_version}

    @app.get("/health", tags=["Sistema"])
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(auth_router.router, prefix="/api")
    app.include_router(registro_router.router, prefix="/api")
    app.include_router(estresse_router.router, prefix="/api")
    app.include_router(alerta_router.router, prefix="/api")

    return app


# Instância global usada por uvicorn (uvicorn src.main:app)
app = criar_app()
