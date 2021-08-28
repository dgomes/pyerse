from datetime import datetime
import logging
import requests
from datetime import date, datetime

from pyerse.comercializador import POTENCIA


class Simulador:
    def __init__(self, potencia, period_start, period_stop=None):
        try:
            self._potencia = POTENCIA.index(potencia)
        except ValueError as err:
            logging.error("Potencia não disponivel!")
            raise err

        def validate(date_str):
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato de data incorrecto, deve ser YYYY-MM-DD")
            return date_str

        self._period_start = validate(period_start)

        if period_stop:
            self._period_stop = validate(period_stop)
        else:
            self._period_stop = date.today().strftime("%Y-%m-%d")

    def _simular(self, ponta, cheias=None, vazio=None):

        if vazio != None:
            ciclo = "3"  # Tri-horário
        elif cheias != None:
            ciclo = "2"  # Bi-horário
        else:
            ciclo = "1"  # Simples

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "simulador.precos.erse.pt",
        }

        data = {
            "pageStartIndex": "0",
            "pageStep": "1",
            "caseType": "3",  # Residencial
            "electSupply": self._potencia,
            "cycle": ciclo,
            "electCalendar": "3",  # "a definir"
            "electCalendarPeriodStart": self._period_start,
            "electCalendarPeriodEnd": self._period_stop,
            "electPonta": ponta,
            "electCheias": cheias if cheias else "",
            "electVazio": vazio if vazio else "",
        }

        logging.debug("Simulation data: %s", data)

        response = requests.post(
            "https://simulador.precos.erse.pt/connectors/simular_eletricidade/",
            headers=headers,
            data=data,
        )

        result = response.json()

        logging.debug(result["Resultados"][0]["Oferta"][0])

        preco_ponta = (
            float(
                result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia"].replace(
                    ",", "."
                )
            )
            * ponta
            if result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia"].replace(
                ",", "."
            )
            != ""
            else 0
        )
        preco_cheias = (
            float(
                result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia2"].replace(
                    ",", "."
                )
            )
            * cheias
            if result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia2"].replace(
                ",", "."
            )
            != ""
            else 0
        )
        preco_vazio = (
            float(
                result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia3"].replace(
                    ",", "."
                )
            )
            * vazio
            if result["Resultados"][0]["Oferta"][0]["PrecoTermoenergia3"].replace(
                ",", "."
            )
            != ""
            else 0
        )
        preco_fixo = float(
            result["Resultados"][0]["Oferta"][0]["PrecoTermoFixo"].replace(",", ".")
        )

        periodo = datetime.strptime(self._period_stop, "%Y-%m-%d") - datetime.strptime(
            self._period_start, "%Y-%m-%d"
        )

        estimativa = (
            preco_ponta + preco_cheias + preco_vazio + preco_fixo * periodo.days
        )

        return (
            f"{result['Resultados'][0]['Oferta'][0]['Comercializador']} - {result['Resultados'][0]['Oferta'][0]['Nome']}",
            estimativa,
        )

    def melhor_tarifa_simples(self, energia):
        return self._simular(ponta=energia)

    def melhor_tarifa_bihorario(self, fora_de_vazio, vazio):
        return self._simular(ponta=fora_de_vazio, cheias=vazio)

    def melhor_tarifa_trihorario(self, ponta, cheias, vazio):
        return self._simular(ponta, cheias, vazio)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    s = Simulador(6.9, "2021-8-1")

    print(s.melhor_tarifa_simples(220))

    print(s.melhor_tarifa_bihorario(120, 100))

    print(s.melhor_tarifa_trihorario(20, 100, 100))
