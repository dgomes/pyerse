""""Helper com periodos horários regulados"""

from enum import Enum


class Periodos_Horarios(Enum):
    """Periodos regulados pela ERSE em https://www.erse.pt/atividade/regulacao/tarifas-e-precos-eletricidade/#periodos-horarios."""

    PONTA = "Ponta"  # aplicável a consumidores de todos os níveis de tensão e a consumidores em baixa tensão normal (BTN) que tenham a tarifa tri-horária.
    CHEIAS = "Cheias"  # aplicável a consumidores de todos os níveis de tensão e a consumidores em BTN que tenham a tarifa tri e bi-horária
    VAZIO_NORMAL = "Vazio Normal"  # aplicável a consumidores de todos os níveis de tensão e a consumidores em BTN que tenham a tarifa tri ou bi-horária. Corresponde ao período em que o preço da energia é mais reduzido
    SUPER_VAZIO = "Super Vazio"  # aplicável a consumidores ligados em baixa tensão especial (BTE), média tensão (MT), alta tensão (AT) e muito alta tensão (MAT).

    def __str__(self):
        """Return nome do periodo."""
        return self.value
