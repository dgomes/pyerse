from datetime import datetime, timezone
from itertools import islice
from zoneinfo import ZoneInfo

import pytest

from pyerse.ciclos import MAPPING, Ciclo_Semanal_Acores, Ciclo_Semanal_Madeira
from pyerse.comercializador import Comercializador, Opcao_Horaria, Plano, Tarifa

REGIONAL = [(name, cycle) for name, cycle in MAPPING.items() if hasattr(cycle, "timezone")]


@pytest.mark.parametrize("name,cycle", REGIONAL)
def test_regional_plans_and_aware_instants(name, cycle):
    utc = datetime(2026, 7, 6, 8, 30, tzinfo=timezone.utc)
    local = utc.astimezone(ZoneInfo(cycle.timezone))
    assert cycle.get_periodo_horario(utc) == cycle.get_periodo_horario(local)
    assert cycle.get_intervalo_periodo_horario(utc) == cycle.get_intervalo_periodo_horario(local)
    named = Comercializador("Regional", 6.9, Opcao_Horaria.TRI_HORARIA, name).plano
    direct = Plano(6.9, Opcao_Horaria.TRI_HORARIA, cycle)
    assert named.tarifa_actual(utc) == direct.tarifa_actual(local)
    assert list(islice(named.intervalo(utc), 3)) == list(islice(direct.intervalo(local), 3))
    assert named.tarifa_actual() in named.tarifas
    assert next(named.intervalo())[0].tzinfo == ZoneInfo(cycle.timezone)


@pytest.mark.parametrize("cycle", [Ciclo_Semanal_Acores, Ciclo_Semanal_Madeira])
@pytest.mark.parametrize(
    "timestamp,season",
    [
        ("2026-05-31T23:59:59", "Novembro a Maio"),
        ("2026-06-01T00:00:00", "Junho a Outubro"),
        ("2026-10-31T23:59:59", "Junho a Outubro"),
        ("2026-11-01T00:00:00", "Novembro a Maio"),
    ],
)
def test_weekly_month_boundaries(cycle, timestamp, season):
    assert cycle.season(datetime.fromisoformat(timestamp)) == season


@pytest.mark.parametrize("cycle", [Ciclo_Semanal_Acores, Ciclo_Semanal_Madeira])
def test_full_day_sunday_and_iterator(cycle):
    sunday = datetime(2026, 7, 5)
    assert cycle.get_intervalo_periodo_horario(sunday.replace(hour=12)) == (
        sunday,
        datetime(2026, 7, 6),
    )
    intervals = cycle.iter_intervalo_periodo_horario(sunday)
    assert next(intervals) == (sunday, datetime(2026, 7, 6))
    assert next(intervals) == (datetime(2026, 7, 6), datetime(2026, 7, 6, 7))
    assert Plano(6.9, Opcao_Horaria.BI_HORARIA, cycle).tarifa_actual(sunday) == Tarifa.VAZIO
