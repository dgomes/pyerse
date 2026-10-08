"""Compare supported cycles with the independently retrieved ERSE chart data."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from pyerse.ciclos import MAPPING
from pyerse.periodos_horarios import Periodos_Horarios as Period

SNAPSHOT = Path(__file__).resolve().parents[1] / "docs/data/erse-horarios-2026-10-08.json"
RECORDS = [row for row in json.loads(SNAPSHOT.read_text()) if row["ciclo"] != "semanal_opcional"]
PERIODS = {
    "ponta": Period.PONTA,
    "cheias": Period.CHEIAS,
    "vazio_normal": Period.VAZIO_NORMAL,
    "super_vazio": Period.SUPER_VAZIO,
}


def minutes(clock):
    hour, minute = map(int, clock.split(":"))
    return hour * 60 + minute


@pytest.mark.parametrize("row", RECORDS)
def test_cycle_against_erse(row):
    region = {"continental": "", "ra_açores": " Açores", "ra_madeira": " Madeira"}[row["região"]]
    title = {"diário": "Diário", "diário_opcional": "Diário Opcional", "semanal": "Semanal"}[
        row["ciclo"]
    ]
    cycle = MAPPING[f"Ciclo {title}{region}"]
    monday = (
        datetime(2026, 7, 6)
        if row["hora_legal"] in ("verão", "junho_outubro")
        else datetime(2026, 1, 5)
    )
    weekdays = {
        None: range(7),
        "segunda_a_sexta": range(5),
        "sábado": [5],
        "domingo": [6],
    }[row["período_horário"]]
    for weekday in weekdays:
        midnight = monday + timedelta(days=weekday)
        for minute in range(1440):
            matches = [
                (PERIODS[period], minutes(start), minutes(stop))
                for period, intervals in row["timestamps"].items()
                for start, stop in intervals
                if minutes(start) <= minute < minutes(stop)
            ]
            assert len(matches) == 1, (row, minute, matches)
            expected, start, stop = matches[0]
            timestamp = midnight + timedelta(minutes=minute)
            assert cycle.get_periodo_horario(timestamp) == expected
            assert cycle.get_intervalo_periodo_horario(timestamp) == (
                midnight + timedelta(minutes=start),
                midnight + timedelta(minutes=stop),
            )
