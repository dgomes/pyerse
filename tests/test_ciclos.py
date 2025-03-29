import pytest
from freezegun import freeze_time

from pyerse.ciclos import Ciclo_Diario, Ciclo_Semanal
from datetime import datetime

@pytest.mark.parametrize("frozen_time, expected_intervalo", [
    ("2025-03-23 00:05:00", (datetime(2025, 3, 23, 0, 0), datetime(2025, 3, 23, 2, 0))),
    ("2025-03-23 15:15:00", (datetime(2025, 3, 23, 6, 0), datetime(2025, 3, 24, 0, 0))),
    ("2025-03-22 12:15:00", (datetime(2025, 3, 22, 9, 30), datetime(2025, 3, 22, 13, 0))),
    ("2025-03-24 20:00:00", (datetime(2025, 3, 24, 18, 30), datetime(2025, 3, 24, 21, 0)))
])
def test_intervalo_semanal(frozen_time, expected_intervalo):
    with freeze_time(frozen_time):

        c = Ciclo_Semanal()
        now = datetime.now()

        assert c.get_intervalo_periodo_horario(now) == expected_intervalo

@pytest.mark.parametrize("frozen_time, expected_intervalo", [
    ("2025-03-23 00:05:00", (datetime(2025, 3, 23, 0, 0), datetime(2025, 3, 23, 2, 0))),
    ("2025-03-22 12:15:00", (datetime(2025, 3, 22, 10, 30), datetime(2025, 3, 22, 18, 0))),
    ("2025-03-24 20:00:00", (datetime(2025, 3, 24, 18, 0), datetime(2025, 3, 24, 20, 30)))
])
def test_intervalo_diario(frozen_time, expected_intervalo):
    with freeze_time(frozen_time):

        c = Ciclo_Diario()
        now = datetime.now()

        assert c.get_intervalo_periodo_horario(now) == expected_intervalo


@pytest.mark.parametrize("frozen_time, expected_intervalo1, expected_intervalo2", [
    ("2025-03-22 23:15:00", (datetime(2025, 3, 22, 22, 0), datetime(2025, 3, 23, 0, 0)), (datetime(2025, 3, 23, 0, 0), datetime(2025, 3, 23, 2, 0))),
    ("2025-03-24 12:00:00", (datetime(2025, 3, 24, 12, 00), datetime(2025, 3, 24, 18, 30)), (datetime(2025, 3, 24, 18, 30), datetime(2025, 3, 24, 21, 0))),
])
def test_get_intervalo_proximo_periodo_horario(frozen_time, expected_intervalo1, expected_intervalo2):
    with freeze_time(frozen_time):

        c = Ciclo_Semanal()
        now = datetime.now()

        iter_intervalo = c.iter_intervalo_periodo_horario(now)

        assert next(iter_intervalo) == expected_intervalo1
        assert next(iter_intervalo) == expected_intervalo2
