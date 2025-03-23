import pytest
from freezegun import freeze_time

from pyerse.ciclos import Ciclo, Ciclo_Semanal
from pyerse.comercializador import Plano, Opcao_Horaria, PlanoException, Tarifa
from datetime import time, datetime

@pytest.mark.parametrize("frozen_time, expected_intervalo", [
    ("2025-03-23 00:05:00", (time(0, 0), time(2, 0))),
    ("2025-03-23 15:15:00", (time(6, 0), time(0, 0))),
    ("2025-03-22 12:15:00", (time(9, 30), time(13, 0))),
    ("2025-03-24 20:00:00", (time(18, 30), time(21, 0)))
])
def test_intervalo_semanal(frozen_time, expected_intervalo):
    with freeze_time(frozen_time):

        c = Ciclo_Semanal()
        now = datetime.now()

        assert c.get_intervalo_periodo_horario(now) == expected_intervalo

@pytest.mark.parametrize("frozen_time, expected_intervalo", [
    ("2025-03-22 23:15:00", (time(0, 0), time(2, 0))),
    ("2025-03-24 12:00:00", (time(18, 30), time(21, 0))),
])
def test_get_intervalo_proximo_periodo_horario(frozen_time, expected_intervalo):
    with freeze_time(frozen_time):

        c = Ciclo_Semanal()
        now = datetime.now()

        assert next(c.get_intervalo_proximo_periodo_horario(now)) == expected_intervalo
