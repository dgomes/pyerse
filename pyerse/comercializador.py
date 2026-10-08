"""Informação por comercializador."""

import logging
from datetime import datetime, time, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

from pyerse.ciclos import MAPPING as CYCLE_MAPPING
from pyerse.ciclos import Ciclo
from pyerse.periodos_horarios import Periodos_Horarios


class Opcao_Horaria(str, Enum):
    """Ciclos de contagem."""

    SIMPLES = "Simples"
    BI_HORARIA = "Bi-Horária"
    TRI_HORARIA = "Tri-Horária"


class Tarifa(str, Enum):
    """Tarifas."""

    PONTA = "Ponta"
    CHEIAS = "Cheias"
    VAZIO = "Vazio"
    FORA_DE_VAZIO = "Fora de Vazio"
    NORMAL = "Normal"


POTENCIA = [
    1.15,
    2.3,
    3.45,
    4.60,
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

IVA_REDUZIDA = 1.06
IVA_INTERMEDIA = 1.13
IVA_NORMAL = 1.23

IMPOSTO_ESPECIAL_CONSUMO = 0.001
CONTRIB_AUDIOVISUAL = 2.85
TAXA_DGEG = 0.07


class PlanoException(Exception):
    """Exceptions lançadas por Plano."""


class Plano:
    """Plano de Energia."""

    def __init__(self, potencia: float, opcao_horaria: Opcao_Horaria, ciclo: Ciclo = None):
        """Inicialização do Plano."""
        self._potencia = potencia if potencia in POTENCIA else None
        self._opcao_horaria = opcao_horaria
        if opcao_horaria != Opcao_Horaria.SIMPLES and ciclo is None:
            raise PlanoException("Ciclo não definido")

        if ciclo and not (isinstance(ciclo, type) and issubclass(ciclo, Ciclo)):
            ciclo = CYCLE_MAPPING[ciclo]
        self._ciclo = ciclo
        self._custo = {}

    def __str__(self):
        """Representação textual do plano."""
        return (
            f"{self._potencia} kVA - {self._opcao_horaria} {self._ciclo() if self._ciclo else ''}"
        )

    @property
    def potencia(self):
        return self._potencia

    @property
    def tarifas(self):
        """Tarifas disponiveis para o plano."""
        if self._opcao_horaria == Opcao_Horaria.SIMPLES:
            return [Tarifa.NORMAL]
        elif self._opcao_horaria == Opcao_Horaria.BI_HORARIA:
            return [Tarifa.VAZIO, Tarifa.FORA_DE_VAZIO]
        elif self._opcao_horaria == Opcao_Horaria.TRI_HORARIA:
            return [Tarifa.VAZIO, Tarifa.CHEIAS, Tarifa.PONTA]

    def tarifa_actual(self, now=None):
        """Tarifa actual."""
        if now is None:
            now = (
                datetime.now(ZoneInfo(self._ciclo.timezone))
                if self._ciclo and hasattr(self._ciclo, "timezone")
                else datetime.now()
            )

        if self._opcao_horaria == Opcao_Horaria.SIMPLES:
            return Tarifa.NORMAL
        elif self._opcao_horaria == Opcao_Horaria.BI_HORARIA:
            return (
                Tarifa.VAZIO
                if self._ciclo.get_periodo_horario(now)
                in [Periodos_Horarios.VAZIO_NORMAL, Periodos_Horarios.SUPER_VAZIO]
                else Tarifa.FORA_DE_VAZIO
            )
        elif self._opcao_horaria == Opcao_Horaria.TRI_HORARIA:
            periodo_actual = self._ciclo.get_periodo_horario(now)
            if periodo_actual in [
                Periodos_Horarios.VAZIO_NORMAL,
                Periodos_Horarios.SUPER_VAZIO,
            ]:
                return Tarifa.VAZIO
            elif periodo_actual == Periodos_Horarios.PONTA:
                return Tarifa.PONTA
            elif periodo_actual == Periodos_Horarios.CHEIAS:
                return Tarifa.CHEIAS

    def intervalo(self, now=None):
        """iterator sobre os Intervalos de tarifa."""
        if now is None:
            now = (
                datetime.now(ZoneInfo(self._ciclo.timezone))
                if self._ciclo and hasattr(self._ciclo, "timezone")
                else datetime.now()
            )

        if self._opcao_horaria == Opcao_Horaria.SIMPLES:
            datetime_start = datetime.combine(now, time(0, 0)) + timedelta(days=1)
            return datetime_start, datetime_start + timedelta(days=1)

        elif self._opcao_horaria in [Opcao_Horaria.BI_HORARIA, Opcao_Horaria.TRI_HORARIA]:
            current_tarifa = self.tarifa_actual(now)
            return_start, return_stop = None, None
            initial = None
            current = False

            for start, stop in self._ciclo.iter_intervalo_periodo_horario(now):
                new_tarifa = self.tarifa_actual(start)
                if initial is None:
                    initial = start  # TODO devia andar para tras

                if new_tarifa != current_tarifa and return_start is None:
                    if not current:
                        current = True
                        yield initial, start
                    return_start = start
                    current_tarifa = new_tarifa

                if new_tarifa != current_tarifa and return_stop is None:
                    return_stop = start

                    yield return_start, return_stop

                    current_tarifa = new_tarifa
                    return_start, return_stop = return_stop, None

    def definir_custo_kWh(self, tarifa: Tarifa, custo: float):
        """Configura o custo em Euros por kWh da tarifa."""
        self._custo[tarifa] = custo

    def definir_custo_potencia(self, custo: float):
        """Configura o custo em Euros por dia da potencia instalada."""
        self._custo[self._potencia] = custo

    def custo_tarifa(self, tarifa: Tarifa):
        return self._custo.get(tarifa, 0)  # TODO exception

    def custo_potencia(self):
        return self._custo[self._potencia]

    def _limiar_iva(self, familia_numerosa=False, dias=30):
        """Limiar de consumo com IVA reduzido, proporcional aos dias faturados."""
        if dias < 0:
            raise PlanoException("Número de dias não pode ser negativo")
        if self._potencia > 6.9:
            return 0.0
        return (300 if familia_numerosa else 200) * dias / 30

    def custo_kWh_actual(
        self,
        kwh_consumidos: float,
        familia_numerosa=False,
        *,
        total_kwh: float | None = None,
        dias=30,
    ):
        """Preço marginal com IVA, segundo as regras de janeiro de 2025.

        Para opções multi-horárias, total_kwh deve incluir todas as tarifas.
        Sem total_kwh, considera-se kwh_consumidos como o consumo total.
        """
        tarifa_actual = self.tarifa_actual()
        try:
            custo_kwh = self._custo[tarifa_actual]
        except KeyError:
            raise PlanoException(f"Sem valor de custo para {tarifa_actual}")
        total = kwh_consumidos if total_kwh is None else total_kwh
        limiar = self._limiar_iva(familia_numerosa, dias)
        iva = IVA_REDUZIDA if self._potencia <= 6.9 and total <= limiar else IVA_NORMAL
        return custo_kwh * iva

    def custo_kWh(
        self,
        tarifa: Tarifa,
        kwh_consumidos: float,
        familia_numerosa=False,
        *,
        total_kwh: float | None = None,
        dias=30,
    ):
        """Custo da energia com IVA, segundo as regras de janeiro de 2025.

        O limite é 200 kWh (300 para famílias numerosas) por 30 dias até
        6,9 kVA. Nas opções multi-horárias, passar total_kwh com a soma de
        todos os períodos para repartir o limite pelo consumo efetivo.
        Sem total_kwh, considera-se kwh_consumidos como o consumo total.
        Não recalcula impostos de períodos anteriores a janeiro de 2025.
        """
        try:
            custo_kwh = self._custo[tarifa]
        except KeyError:
            raise PlanoException(f"Sem valor de custo para {tarifa}")
        total = kwh_consumidos if total_kwh is None else total_kwh
        if kwh_consumidos < 0 or total < kwh_consumidos:
            raise PlanoException("Consumo total deve ser não negativo e incluir a tarifa")
        limiar = self._limiar_iva(familia_numerosa, dias)
        reduzido = min(kwh_consumidos, limiar * kwh_consumidos / total) if total else 0.0
        return round(reduzido * custo_kwh * IVA_REDUZIDA, 2) + round(
            (kwh_consumidos - reduzido) * custo_kwh * IVA_NORMAL, 2
        )

    def custo_kWh_final(
        self,
        tarifa: Tarifa,
        kwh_consumidos: float,
        familia_numerosa=False,
        *,
        total_kwh: float | None = None,
        dias=30,
    ):
        """Custo com IVA e imposto especial de consumo (IEC)."""
        return (
            self.custo_kWh(tarifa, kwh_consumidos, familia_numerosa, total_kwh=total_kwh, dias=dias)
            + kwh_consumidos * IMPOSTO_ESPECIAL_CONSUMO * IVA_NORMAL
        )

    def custos_fixos(self, dias: int):
        """Custos fixos em Euros."""
        if self._potencia <= 3.45:
            logging.warning(
                "Potencia igual ou inferior a 3.45 com desconto sobre o valor total da potencia!"
            )
        custo_potencia = (
            dias
            * self._custo[self._potencia]
            * (IVA_REDUZIDA if self._potencia <= 3.45 else IVA_NORMAL)
        )

        return (
            round(custo_potencia, 2)
            + round(CONTRIB_AUDIOVISUAL * IVA_REDUZIDA, 2)
            + round(TAXA_DGEG * IVA_NORMAL, 2)
        )


class Comercializador:
    """Representação de um Comercializador."""

    def __init__(self, nome: str, potencia: float, horario: Opcao_Horaria, ciclo: str = None):
        """Configuração de um plano para o comercializador."""
        self._name = nome
        self._plano = Plano(potencia, horario, CYCLE_MAPPING[ciclo])

    def __str__(self) -> str:
        """Nome do operador e respectivo plano."""
        return f"{self._name} - {self._plano}"

    @classmethod
    def potencias(cls):
        """Potencias disponiveis."""
        return POTENCIA

    @classmethod
    def opcao_horaria(cls):
        """Opções horárias."""
        return [
            Opcao_Horaria.SIMPLES,
            Opcao_Horaria.BI_HORARIA,
            Opcao_Horaria.TRI_HORARIA,
        ]

    @classmethod
    def opcao_ciclo(cls):
        """Opções de ciclo para opção bi-horaria ou tri-horaria."""
        return CYCLE_MAPPING.keys()

    @property
    def plano(self):
        """Plano do comercializador."""
        return self._plano
