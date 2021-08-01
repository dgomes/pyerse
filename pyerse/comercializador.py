"""Informação por comercializador"""
import logging
from enum import Enum
from datetime import datetime
from pyerse.periodos_horarios import Periodos_Horarios
from pyerse.ciclos import Ciclo, Ciclo_Diario, Ciclo_Semanal


class Opcao_Horaria(Enum):
    """Ciclos de contagem"""

    SIMPLES = "Simples"
    BI_HORARIA = "Bi-Horária"
    TRI_HORARIA = "Tri-Horária"


class Tarifa(Enum):
    """Tarifas"""

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
    pass

class Plano:
    def __init__(self, potencia: float, opcao_horaria: Opcao_Horaria, ciclo: Ciclo = None):
        self._potencia = potencia if potencia in POTENCIA else None
        self._opcao_horaria = opcao_horaria
        if opcao_horaria != Opcao_Horaria.SIMPLES and ciclo == None:
            raise PlanoException("Ciclo não definido")

        self._ciclo = ciclo
        self._custo = {}

    def __str__(self):
        return f"{self._potencia} kVA - {self._opcao_horaria} {self._ciclo if self._ciclo else ''}"

    @property
    def tarifa_actual(self):
        now = datetime.now()

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

    def definir_custo_kWh(self, tarifa: Tarifa, custo: float):
        self._custo[tarifa] = custo
    
    def definir_custo_potencia(self, custo: float):
        self._custo[self._potencia] = custo

    def custo_kWh_actual(self, kwh_consumidos: float, familia_numerosa = False):
        """Custo com IVA com base em https://www.erse.pt/media/pzievesl/ersexplica_aplicação-do-iva.pdf"""
        tarifa_actual = self.tarifa_actual
        
        try:
            custo_kwh = self._custo[tarifa_actual]
        except KeyError:
            raise PlanoException(f"Sem valor de custo para {tarifa_actual}")

        if self._potencia > 6.9:
            return custo_kwh * IVA_NORMAL
        
        def desconto(plafond):
            if kwh_consumidos > plafond:
                return custo_kwh * IVA_NORMAL
            else:
                return custo_kwh * IVA_INTERMEDIA


        if self._opcao_horaria == Opcao_Horaria.SIMPLES:
            return desconto(150 if familia_numerosa else 100)

        if self._opcao_horaria == Opcao_Horaria.BI_HORARIA:
            if tarifa_actual == Tarifa.VAZIO:
                return desconto(60 if familia_numerosa else 40)
            else:
                return desconto(90 if familia_numerosa else 60)

        if self._opcao_horaria == Opcao_Horaria.TRI_HORARIA:
            if tarifa_actual == Tarifa.CHEIAS:
                return desconto(64.3 if familia_numerosa else 42.9)
            elif tarifa_actual == Tarifa.PONTA:
                return desconto(25.7 if familia_numerosa else 17.1)
            elif tarifa_actual == Tarifa.VAZIO:
                return desconto(60 if familia_numerosa else 40)

    def custo_kWh(self, tarifa: Tarifa, kwh_consumidos: float, familia_numerosa = False):
        try:
            custo_kwh = self._custo[tarifa]
        except KeyError:
            raise PlanoException(f"Sem valor de custo para {tarifa}")        

        def desconto(plafond):
            if kwh_consumidos > plafond:
                return round(plafond * custo_kwh * IVA_INTERMEDIA, 2) + round((kwh_consumidos-plafond) * custo_kwh * IVA_NORMAL, 2)
            else:
                return round(kwh_consumidos * custo_kwh * IVA_INTERMEDIA, 2)

        if self._opcao_horaria == Opcao_Horaria.SIMPLES:
            return desconto(150 if familia_numerosa else 100)

        if self._opcao_horaria == Opcao_Horaria.BI_HORARIA:
            if tarifa == Tarifa.VAZIO:
                return desconto(60 if familia_numerosa else 40)
            else:
                return desconto(90 if familia_numerosa else 60)

        if self._opcao_horaria == Opcao_Horaria.TRI_HORARIA:
            if tarifa == Tarifa.CHEIAS:
                return desconto(64.3 if familia_numerosa else 42.9)
            elif tarifa == Tarifa.PONTA:
                return desconto(25.7 if familia_numerosa else 17.1)
            elif tarifa == Tarifa.VAZIO:
                return desconto(60 if familia_numerosa else 40)

    def custos_fixos(self, dias: int, kwh_consumidos: float):
        if self._potencia <= 3.45:
            logging.warning("Potencia inferior a 3.45 com desconto sobre o valor total da potencia!")
        custo_potencia = dias * self._custo[self._potencia] * (IVA_REDUZIDA if self._potencia <= 3.45 else IVA_NORMAL)
        imposto_especial_consumo = kwh_consumidos * IMPOSTO_ESPECIAL_CONSUMO * IVA_NORMAL

        return round(custo_potencia, 2) + round(imposto_especial_consumo, 2) + round(CONTRIB_AUDIOVISUAL*IVA_REDUZIDA, 2) + round(TAXA_DGEG*IVA_NORMAL, 2)

class Comercializador:
    def __init__(self, potencia, horario: Opcao_Horaria, ciclo: Ciclo = None):
        self._plano = Plano(potencia, horario, ciclo)

    @classmethod
    def potencias(cls):
        return POTENCIA

    @classmethod
    def opcao_horaria(cls):
        return [Opcao_Horaria.SIMPLES, Opcao_Horaria.BI_HORARIA, Opcao_Horaria.TRI_HORARIA]

    @classmethod
    def opcao_ciclo(cls):
        return [Ciclo_Diario, Ciclo_Semanal]

    @property
    def plano(self):
        return self._plano
