from unittest.mock import Mock

import pytest
from freezegun import freeze_time
from requests import RequestException

from pyerse.simulador import Simulador


@pytest.mark.parametrize(
    "method, energy, cycle, prices, expected",
    [
        ("melhor_tarifa_simples", (100,), "1", ("0,20", "", ""), 23),
        ("melhor_tarifa_bihorario", (100, 50), "2", ("0,20", "0,10", ""), 28),
        ("melhor_tarifa_trihorario", (10, 100, 50), "3", ("0,30", "0,20", "0,10"), 31),
        ("melhor_tarifa_trihorario", (0, 0, 0), "3", ("0,30", "0,20", "0,10"), 3),
        ("melhor_tarifa_bihorario", (0, 0), "2", ("0,20", "0,10", ""), 3),
    ],
)
def test_simulation_request_and_estimate(monkeypatch, method, energy, cycle, prices, expected):
    offer = dict(zip(("PrecoTermoenergia", "PrecoTermoenergia2", "PrecoTermoenergia3"), prices))
    offer.update(PrecoTermoFixo="0,30", Comercializador="Supplier", Nome="Offer")
    post = Mock(return_value=Mock(json=Mock(return_value={"Resultados": [{"Oferta": [offer]}]})))
    monkeypatch.setattr("pyerse.simulador.requests.post", post)

    simulator = Simulador(6.9, "2025-01-01", "2025-01-11")
    name, estimate = getattr(simulator, method)(*energy)

    assert name == "Supplier - Offer"
    assert estimate == pytest.approx(expected)
    post.assert_called_once_with(
        "https://simulador.precos.erse.pt/connectors/simular_eletricidade/",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "simulador.precos.erse.pt",
        },
        data={
            "pageStartIndex": "0",
            "pageStep": "1",
            "caseType": "3",
            "electSupply": 5,
            "cycle": cycle,
            "electCalendar": "3",
            "electCalendarPeriodStart": "2025-01-01",
            "electCalendarPeriodEnd": "2025-01-11",
            "electPonta": energy[0],
            "electCheias": energy[1] if len(energy) > 1 and energy[1] else "",
            "electVazio": energy[2] if len(energy) > 2 and energy[2] else "",
        },
    )


@pytest.mark.parametrize("start, stop", [("bad", "2025-01-11"), ("2025-01-01", "2025-02-30")])
def test_invalid_dates(start, stop):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        Simulador(6.9, start, stop)


def test_invalid_power():
    with pytest.raises(ValueError):
        Simulador(7, "2025-01-01")


@freeze_time("2025-01-11")
def test_default_end_date_and_network_error(monkeypatch):
    post = Mock(side_effect=RequestException("offline"))
    monkeypatch.setattr("pyerse.simulador.requests.post", post)
    with pytest.raises(RequestException, match="offline"):
        Simulador(6.9, "2025-01-01").melhor_tarifa_simples(100)
    assert post.call_args.kwargs["data"]["electCalendarPeriodEnd"] == "2025-01-11"


def test_invalid_json_is_propagated(monkeypatch):
    monkeypatch.setattr(
        "pyerse.simulador.requests.post",
        Mock(return_value=Mock(json=Mock(side_effect=ValueError("invalid JSON")))),
    )
    with pytest.raises(ValueError, match="invalid JSON"):
        Simulador(6.9, "2025-01-01", "2025-01-11").melhor_tarifa_simples(100)
