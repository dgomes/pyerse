from freezegun import freeze_time

from pyerse.ciclos import Ciclo, Ciclo_Semanal
from pyerse.comercializador import Plano, Opcao_Horaria, PlanoException, Tarifa


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
