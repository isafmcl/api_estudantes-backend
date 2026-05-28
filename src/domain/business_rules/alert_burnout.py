"""AlertBurnout (RN-003): detecção de risco de burnout (US14, DAS §4.3)."""

from typing import Optional

from src.domain.entities.score_estresse import ScoreEstresse


class AlertBurnout:
    """RN-003: 3+ dias consecutivos com score > 70 indicam risco de burnout."""

    LIMIAR_SCORE = 70
    DIAS_CONSECUTIVOS_NECESSARIOS = 3

    def detectar(self, historico_desc: list[ScoreEstresse]) -> Optional[int]:
        """Recebe histórico em ordem decrescente (mais recente primeiro).

        Retorna o número de dias consecutivos de risco se >= 3, senão None.
        """
        dias_consecutivos = 0

        for score in historico_desc:
            if score.score is not None and score.score > self.LIMIAR_SCORE:
                dias_consecutivos += 1
            else:
                break  # quebrou a sequência

        if dias_consecutivos >= self.DIAS_CONSECUTIVOS_NECESSARIOS:
            return dias_consecutivos
        return None
