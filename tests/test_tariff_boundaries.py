from datetime import datetime

import pytest
from freezegun import freeze_time

from pyerse.ciclos import Ciclo_Diario, Ciclo_Semanal
from pyerse.comercializador import Comercializador, Opcao_Horaria, Plano, PlanoException, Tarifa


@pytest.mark.parametrize("family", [False, True])
@pytest.mark.parametrize(
    "option, tariff, hour, limit, family_limit",
    [
        (Opcao_Horaria.SIMPLES, Tarifa.NORMAL, 12, 100, 150),
        (Opcao_Horaria.BI_HORARIA, Tarifa.VAZIO, 3, 40, 60),
        (Opcao_Horaria.BI_HORARIA, Tarifa.FORA_DE_VAZIO, 12, 60, 90),
        (Opcao_Horaria.TRI_HORARIA, Tarifa.VAZIO, 3, 40, 60),
        (Opcao_Horaria.TRI_HORARIA, Tarifa.CHEIAS, 12, 42.9, 64.3),
        (Opcao_Horaria.TRI_HORARIA, Tarifa.PONTA, 10, 17.1, 25.7),
    ],
)
def test_consumption_cost_thresholds(family, option, tariff, hour, limit, family_limit):
    plan = Plano(6.9, option, Ciclo_Semanal)
    plan.definir_custo_kWh(tariff, 0.2)
    threshold = family_limit if family else limit
    with freeze_time(datetime(2025, 1, 6, hour)):
        assert plan.custo_kWh_actual(threshold, family) == pytest.approx(0.226)
        assert plan.custo_kWh_actual(threshold + 1, family) == pytest.approx(0.246)
    assert plan.custo_kWh(tariff, 0, family) == 0
    assert plan.custo_kWh(tariff, threshold, family) == round(threshold * 0.226, 2)
    assert plan.custo_kWh(tariff, threshold + 10, family) == pytest.approx(
        round(threshold * 0.226, 2) + 2.46
    )
    assert plan.custo_kWh_final(tariff, 10, family) == pytest.approx(2.26 + 0.0123)


def test_high_power_and_missing_prices():
    plan = Plano(10.35, Opcao_Horaria.SIMPLES)
    with pytest.raises(PlanoException, match="Sem valor de custo"):
        plan.custo_kWh_actual(0)
    with pytest.raises(PlanoException, match="Sem valor de custo"):
        plan.custo_kWh(Tarifa.NORMAL, 10)
    plan.definir_custo_kWh(Tarifa.NORMAL, 0.2)
    assert plan.custo_kWh_actual(0) == pytest.approx(0.246)
    assert plan.custo_tarifa(Tarifa.NORMAL) == 0.2
    assert plan.custo_tarifa(Tarifa.PONTA) == 0
    plan.definir_custo_potencia(0.3)
    assert plan.custo_potencia() == 0.3
    assert plan.potencia == 10.35


@pytest.mark.parametrize("option", [Opcao_Horaria.BI_HORARIA, Opcao_Horaria.TRI_HORARIA])
def test_cycle_required(option):
    with pytest.raises(PlanoException, match="Ciclo não definido"):
        Plano(6.9, option)


@pytest.mark.parametrize(
    "option, tariffs",
    [
        (Opcao_Horaria.SIMPLES, [Tarifa.NORMAL]),
        (Opcao_Horaria.BI_HORARIA, [Tarifa.VAZIO, Tarifa.FORA_DE_VAZIO]),
        (Opcao_Horaria.TRI_HORARIA, [Tarifa.VAZIO, Tarifa.CHEIAS, Tarifa.PONTA]),
    ],
)
def test_plan_tariffs_and_named_cycle(option, tariffs):
    plan = Plano(6.9, option, "Ciclo Diário")
    assert plan.tarifas == tariffs
    assert "Ciclo Diário" in str(plan)
    assert plan.tarifa_actual(datetime(2025, 1, 6, 3)) == tariffs[0]


def test_supplier_public_options():
    supplier = Comercializador("Supplier", 6.9, Opcao_Horaria.BI_HORARIA, "Ciclo Semanal")
    assert isinstance(supplier.plano, Plano)
    assert supplier.plano.potencia == 6.9
    assert str(supplier).startswith("Supplier - 6.9 kVA")
    assert Comercializador.opcao_horaria() == list(Opcao_Horaria)
    assert {"Ciclo Diário", "Ciclo Semanal"} <= set(Comercializador.opcao_ciclo())
    assert Comercializador.potencias() == [
        1.15,
        2.3,
        3.45,
        4.6,
        5.75,
        6.9,
        10.35,
        13.8,
        17.25,
        20.7,
        27.6,
        34.5,
        41.4,
    ]


def test_daily_interval_merges_empty_periods():
    plan = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Diario)
    intervals = plan.intervalo(datetime(2025, 1, 6, 22, 30))
    assert next(intervals) == (datetime(2025, 1, 6, 22), datetime(2025, 1, 7, 8))
    assert next(intervals) == (datetime(2025, 1, 7, 8), datetime(2025, 1, 7, 22))
