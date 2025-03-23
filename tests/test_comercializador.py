import pytest 
from datetime import time, datetime
from freezegun import freeze_time

from pyerse.ciclos import Ciclo, Ciclo_Semanal
from pyerse.comercializador import Plano, Opcao_Horaria, PlanoException, Tarifa

@pytest.mark.parametrize("frozen_time, expected_tarifa, expected_intervalo", [
    ("2025-03-23 00:05:00", Tarifa.VAZIO, (time(0, 0), time(2, 0))),
    ("2025-03-23 15:15:00", Tarifa.VAZIO, (time(6, 0), time(0, 0))),
    ("2025-03-22 12:15:00", Tarifa.FORA_DE_VAZIO, (time(9, 30), time(13, 0))),
    ("2025-03-24 20:00:00", Tarifa.FORA_DE_VAZIO, (time(18, 30), time(21, 0)))
])
def test_intervalo_bi_horario_semanal(frozen_time, expected_tarifa, expected_intervalo):
    with freeze_time(frozen_time):
        p = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Semanal)

        assert p.tarifa_actual() == expected_tarifa
        assert p.tarifa_actual_intervalo() == expected_intervalo

@pytest.mark.parametrize("frozen_time, expected_tarifa, expected_intervalo", [
    ("2025-03-23 00:05:00", Tarifa.VAZIO, (time(0, 0), time(2, 0))),
    ("2025-03-23 15:15:00", Tarifa.VAZIO, (time(6, 0), time(0, 0))),
    ("2025-03-22 12:15:00", Tarifa.CHEIAS, (time(9, 30), time(13, 0))),
    ("2025-03-24 20:00:00", Tarifa.PONTA, (time(18, 30), time(21, 0)))
])
def test_intervalo_bi_horario_semanal(frozen_time, expected_tarifa, expected_intervalo):
    with freeze_time(frozen_time):
        p = Plano(6.9, Opcao_Horaria.TRI_HORARIA, Ciclo_Semanal)

        assert p.tarifa_actual() == expected_tarifa
        assert p.tarifa_actual_intervalo() == expected_intervalo

@pytest.mark.parametrize("frozen_time, expected_tarifa, expected_intervalo, expected_new_tarifa", [
    ("2025-03-24 00:05:00", Tarifa.VAZIO, (datetime(2025, 3, 24, 7, 0), datetime(2025, 3, 25, 0, 0)), Tarifa.FORA_DE_VAZIO),
    ("2025-03-24 15:15:00", Tarifa.FORA_DE_VAZIO, (datetime(2025, 3, 25, 0, 0), datetime(2025, 3, 25, 7, 0)), Tarifa.VAZIO),
])
def test_tarifa_proximo_intervalo_bi_horario(frozen_time, expected_tarifa, expected_intervalo, expected_new_tarifa):
    with freeze_time(frozen_time):
        p = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Semanal)

        assert p.tarifa_actual() == expected_tarifa
        (start, stop) = next(p.proximo_intervalo())
        assert (start, stop) == expected_intervalo
        print(start)
        assert p.tarifa_actual(start) == expected_new_tarifa


@pytest.mark.parametrize("frozen_time, expected_tarifa, expected_intervalo, expected_new_tarifa", [
    ("2025-03-24 00:05:00", Tarifa.VAZIO, (datetime(2025, 3, 24, 7, 0), datetime(2025, 3, 24, 9, 30)), Tarifa.CHEIAS),
    ("2025-03-24 15:15:00", Tarifa.CHEIAS, (datetime(2025, 3, 24, 18, 30), datetime(2025, 3, 24, 21, 0)), Tarifa.PONTA),
])
def test_tarifa_proximo_intervalo_tri_horario(frozen_time, expected_tarifa, expected_intervalo, expected_new_tarifa):
    with freeze_time(frozen_time):
        p = Plano(6.9, Opcao_Horaria.TRI_HORARIA, Ciclo_Semanal)

        assert p.tarifa_actual() == expected_tarifa
        (start, stop) = next(p.proximo_intervalo())
        assert (start, stop) == expected_intervalo
        assert p.tarifa_actual(start) == expected_new_tarifa



def compare_euro(a, b, precision=2):
    return round(a, precision) == round(b, precision)


def test_custo_simples():
    p = Plano(6.9, Opcao_Horaria.SIMPLES)
    p.definir_custo_kWh(Tarifa.NORMAL, 0.100)

    assert p.tarifa_actual() == Tarifa.NORMAL

    assert round(p.custo_kWh_actual(0), 3) == 0.113


@freeze_time("2021-08-04 00:00:00")
def test_custo_bi_horario():
    p = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Semanal)
    p.definir_custo_kWh(Tarifa.VAZIO, 0.100)

    assert p.tarifa_actual() == Tarifa.VAZIO

    assert round(p.custo_kWh_actual(0), 3) == 0.113

    assert round(p.custo_kWh_actual(70), 3) == 0.123

    assert round(p.custo_kWh_actual(50, True), 3) == 0.113


def test_custo_exemplo_1():
    p = Plano(3.45, Opcao_Horaria.SIMPLES)
    p.definir_custo_kWh(Tarifa.NORMAL, 0.1486)
    p.definir_custo_potencia(0.1660)

    assert compare_euro(p.custo_kWh(Tarifa.NORMAL, 160), 16.79 + 10.97)
    assert compare_euro(p.custos_fixos(30), 5.28 + 3.02 + 0.09)


def test_custo_exemplo_2():
    p = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Semanal)
    p.definir_custo_kWh(Tarifa.FORA_DE_VAZIO, 0.1815)
    p.definir_custo_kWh(Tarifa.VAZIO, 0.0958)
    p.definir_custo_potencia(0.3147)

    assert compare_euro(p.custo_kWh(Tarifa.FORA_DE_VAZIO, 170), 12.31 + 24.56)
    assert compare_euro(p.custo_kWh(Tarifa.VAZIO, 80), 4.33 + 4.71)

    assert compare_euro(p.custos_fixos(30), 10.92 + 0.69 + 3.02 + 0.09)


def test_custo_exemplo_3():
    p = Plano(6.9, Opcao_Horaria.BI_HORARIA, Ciclo_Semanal)
    p.definir_custo_kWh(Tarifa.FORA_DE_VAZIO, 0.1815)
    p.definir_custo_kWh(Tarifa.VAZIO, 0.0958)
    p.definir_custo_potencia(0.3147)

    assert compare_euro(
        p.custo_kWh(Tarifa.FORA_DE_VAZIO, 170, familia_numerosa=True), 18.46 + 17.86
    )
    assert compare_euro(
        p.custo_kWh(Tarifa.VAZIO, 80, familia_numerosa=True), 6.50 + 2.36
    )
    assert compare_euro(p.custos_fixos(30), 10.92 + 0.69 + 3.02 + 0.09)
