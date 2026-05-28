"""EventBus: barramento de eventos in-memory (Observer).

Implementação síncrona simples e suficiente para o escopo atual.
Pode ser substituída por implementação assíncrona (RabbitMQ, Redis Streams)
sem impacto no domínio.
"""

from collections import defaultdict
from typing import Callable, Type, TypeVar

T = TypeVar("T")


class EventBus:
    """Publicador/assinante para eventos de domínio."""

    def __init__(self) -> None:
        self._handlers: dict[Type, list[Callable]] = defaultdict(list)

    def inscrever(self, tipo_evento: Type[T], handler: Callable[[T], None]) -> None:
        self._handlers[tipo_evento].append(handler)

    def publicar(self, evento: T) -> None:
        for handler in self._handlers[type(evento)]:
            try:
                handler(evento)
            except Exception as e:  # noqa: BLE001
                # Falha em um handler não deve quebrar a publicação para outros.
                # Em produção, logar com structured logging.
                print(f"[EventBus] handler {handler.__name__} falhou: {e}")


# Singleton de conveniência. Em testes, instanciar EventBus diretamente.
event_bus = EventBus()
