"""Value Objects: tipos imutáveis com significado semântico (DAS §4.3 Domínio).

Estes enums representam os valores possíveis para cada variável monitorada.
São objetos sem identidade, apenas com significado de domínio.
"""

from enum import Enum


class NivelHumor(int, Enum):
    """Escala de humor de 1 (Muito Ruim) a 5 (Muito Bom). US03."""

    MUITO_RUIM = 1
    RUIM = 2
    REGULAR = 3
    BOM = 4
    MUITO_BOM = 5


class QualidadeSono(str, Enum):
    """Classificação subjetiva da qualidade do sono. US05."""

    RUIM = "ruim"
    REGULAR = "regular"
    OTIMO = "otimo"


class QualidadeAlimentacao(str, Enum):
    """Classificação da alimentação do dia. US06."""

    RUIM = "ruim"
    REGULAR = "regular"
    OTIMA = "otima"


class NivelAtividadeFisica(str, Enum):
    """Nível de atividade física do dia. US07."""

    NULA = "nula"
    LEVE = "leve"
    MODERADA = "moderada"
    PESADA = "pesada"


class QualidadeInteracaoSocial(str, Enum):
    """Qualidade percebida das interações sociais do dia. US08."""

    NULA = "nula"
    RUIM = "ruim"
    NEUTRA = "neutra"
    BOA = "boa"


class NivelEstresse(str, Enum):
    """Faixas de classificação do score de estresse calculado (RN-001)."""

    BAIXO = "baixo"
    MODERADO = "moderado"
    ELEVADO = "elevado"
    CRITICO = "critico"
    INDEFINIDO = "indefinido"


class TipoAlerta(str, Enum):
    """Tipos de alerta emitidos pelo sistema."""

    BURNOUT = "burnout"
    SONO_INSUFICIENTE = "sono_insuficiente"
    INFORMATIVO = "informativo"
