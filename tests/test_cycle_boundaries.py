from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from pyerse.ciclos import Ciclo, Ciclo_Diario, Ciclo_Semanal
from pyerse.periodos_horarios import Periodos_Horarios as Period


@pytest.mark.parametrize(
    "timestamp, summer",
    [
        ("2025-03-29T23:59:59", False),
        ("2025-03-30T00:00:00", True),
        ("2025-10-25T23:59:59", True),
        ("2025-10-26T00:00:00", False),
    ],
)
@pytest.mark.parametrize("timezone", [None, ZoneInfo("Europe/Lisbon")])
def test_season_boundaries(timestamp, summer, timezone):
    assert Ciclo.is_summer(datetime.fromisoformat(timestamp).replace(tzinfo=timezone)) is summer


@pytest.mark.parametrize(
    "cycle, day, boundaries",
    [
        (
            Ciclo_Semanal,
            "2025-07-07",
            [
                (0, 0, Period.VAZIO_NORMAL),
                (2, 0, Period.SUPER_VAZIO),
                (6, 0, Period.VAZIO_NORMAL),
                (7, 0, Period.CHEIAS),
                (9, 15, Period.PONTA),
                (12, 15, Period.CHEIAS),
            ],
        ),
        (
            Ciclo_Semanal,
            "2025-07-05",
            [
                (0, 0, Period.VAZIO_NORMAL),
                (2, 0, Period.SUPER_VAZIO),
                (6, 0, Period.VAZIO_NORMAL),
                (9, 0, Period.CHEIAS),
                (14, 0, Period.VAZIO_NORMAL),
                (20, 0, Period.CHEIAS),
                (22, 0, Period.VAZIO_NORMAL),
            ],
        ),
        (
            Ciclo_Semanal,
            "2025-07-06",
            [(0, 0, Period.VAZIO_NORMAL), (2, 0, Period.SUPER_VAZIO), (6, 0, Period.VAZIO_NORMAL)],
        ),
        (
            Ciclo_Diario,
            "2025-07-06",
            [
                (0, 0, Period.VAZIO_NORMAL),
                (2, 0, Period.SUPER_VAZIO),
                (6, 0, Period.VAZIO_NORMAL),
                (8, 0, Period.CHEIAS),
                (10, 30, Period.PONTA),
                (13, 0, Period.CHEIAS),
                (19, 30, Period.PONTA),
                (21, 0, Period.CHEIAS),
                (22, 0, Period.VAZIO_NORMAL),
            ],
        ),
        (
            Ciclo_Diario,
            "2025-01-05",
            [
                (0, 0, Period.VAZIO_NORMAL),
                (2, 0, Period.SUPER_VAZIO),
                (6, 0, Period.VAZIO_NORMAL),
                (8, 0, Period.CHEIAS),
                (9, 0, Period.PONTA),
                (10, 30, Period.CHEIAS),
                (18, 0, Period.PONTA),
                (20, 30, Period.CHEIAS),
                (22, 0, Period.VAZIO_NORMAL),
            ],
        ),
    ],
)
def test_period_transition_endpoints(cycle, day, boundaries):
    midnight = datetime.fromisoformat(day).replace(tzinfo=ZoneInfo("Europe/Lisbon"))
    for index, (hour, minute, expected) in enumerate(boundaries):
        start = midnight.replace(hour=hour, minute=minute)
        if index + 1 < len(boundaries):
            next_hour, next_minute, _ = boundaries[index + 1]
            stop = midnight.replace(hour=next_hour, minute=next_minute)
        else:
            stop = midnight + timedelta(days=1)
        for timestamp in (start, stop - timedelta(microseconds=1)):
            assert cycle.get_periodo_horario(timestamp) == expected
            assert cycle.get_intervalo_periodo_horario(timestamp) == (start, stop)


@pytest.mark.parametrize(
    "hour, expected",
    [(21, False), (22, True), (23, True), (0, True), (5, True), (6, False)],
)
def test_time_range_crosses_midnight(hour, expected):
    assert Ciclo.in_time_range(22, 0, datetime(2025, 1, 1, hour), 6, 0) is expected


def test_period_display_name():
    assert str(Period.VAZIO_NORMAL) == "Vazio Normal"
