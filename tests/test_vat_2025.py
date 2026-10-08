"""Current consumption VAT, including the ERSE multi-tariff example."""

import pytest

from pyerse.comercializador import Opcao_Horaria, Plano, PlanoException, Tarifa


def plan(power=6.9, option=Opcao_Horaria.SIMPLES):
    result = Plano(power, option, "Ciclo Diário")
    for tariff in result.tarifas:
        result.definir_custo_kWh(tariff, 0.2)
    return result


@pytest.mark.parametrize("power", [1.15, 6.9, 10.35])
@pytest.mark.parametrize("kwh", [0, 100, 200, 250])
def test_allowance_and_power_boundary(power, kwh):
    reduced = min(kwh, 200) if power <= 6.9 else 0
    expected = round(reduced * 0.2 * 1.06, 2) + round((kwh - reduced) * 0.2 * 1.23, 2)
    assert plan(power).custo_kWh_final(Tarifa.NORMAL, kwh) == pytest.approx(
        expected + kwh * 0.001 * 1.23
    )


def test_erse_multitariff_example():
    p = plan(option=Opcao_Horaria.BI_HORARIA)
    p.definir_custo_kWh(Tarifa.VAZIO, 0.1)
    assert p.custo_kWh_final(Tarifa.FORA_DE_VAZIO, 252, total_kwh=350) == pytest.approx(
        30.53 + 26.57 + 0.30996
    )
    assert p.custo_kWh_final(Tarifa.VAZIO, 98, total_kwh=350) == pytest.approx(
        5.94 + 5.17 + 0.12054
    )


@pytest.mark.parametrize("days,kwh,energy", [(42, 280, 59.36), (15, 150, 33.5), (0, 50, 12.3)])
def test_billing_days(days, kwh, energy):
    assert plan().custo_kWh_final(Tarifa.NORMAL, kwh, dias=days) == pytest.approx(
        energy + kwh * 0.001 * 1.23
    )


def test_large_family_allowance():
    assert plan().custo_kWh(Tarifa.NORMAL, 350, True) == pytest.approx(63.6 + 12.3)


def test_three_tariffs_share_one_allowance():
    p = plan(option=Opcao_Horaria.TRI_HORARIA)
    assert sum(p.custo_kWh_final(t, 100, total_kwh=300) for t in p.tarifas) == pytest.approx(
        plan().custo_kWh_final(Tarifa.NORMAL, 300), abs=0.02
    )


@pytest.mark.parametrize("kwh,total,days", [(-1, 100, 30), (100, 50, 30), (100, 100, -1)])
def test_invalid_billing_inputs(kwh, total, days):
    with pytest.raises(PlanoException):
        plan().custo_kWh_final(Tarifa.NORMAL, kwh, total_kwh=total, dias=days)


@pytest.mark.parametrize("family,expected", [(False, 55.0075), (True, 53.3075)])
def test_large_family_is_explicit_opt_in(family, expected):
    assert plan().custo_kWh_final(Tarifa.NORMAL, 250, familia_numerosa=family) == pytest.approx(
        expected
    )


def test_large_family_above_power_limit():
    assert plan(10.35).custo_kWh_final(Tarifa.NORMAL, 250, familia_numerosa=True) == pytest.approx(
        61.8075
    )
