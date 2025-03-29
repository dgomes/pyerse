""""Helper com ciclos"""

from datetime import time, datetime, timedelta

from pyerse.periodos_horarios import Periodos_Horarios as ph

class CicloException(Exception):
    """Exceptions lançadas por Ciclo."""
    pass

class Ciclo:
    """Estão previstos dois ciclos: ciclo diário (os períodos horários são iguais em todos os dias do ano) e ciclo semanal (os períodos horários diferem entre dias úteis e fim de semana).

        Mais informações em: https://www.erse.pt/atividade/regulacao/tarifas-e-precos-eletricidade/#periodos-horarios
    """

    @classmethod
    def in_time_range(cls, hour_start, minute_start, t, hour_stop, minute_stop):
        if hour_stop < hour_start:
            return not (
                time(hour_stop, minute_stop)
                <= t.time()
                < time(hour_start, minute_start)
            )
        return time(hour_start, minute_start) <= t.time() < time(hour_stop, minute_stop)

    @classmethod
    def is_summer(cls, time):
        # Hora legal de Verão começa no ultimo Domingo de Março e acaba no ultimo de Outubro
        # https://docs.python.org/3.3/library/datetime.html
        d = datetime(time.year, 4, 1)
        i_verao = d - timedelta(days=d.weekday() + 1)
        d = datetime(time.year, 11, 1)
        f_verao = d - timedelta(days=d.weekday() + 1)
        if i_verao <= time.replace(tzinfo=None) < f_verao:
            return True
        return False


    @classmethod
    def get_periodo_horario(cls, time):
        """Retorna o Periodo Horario em que nos encontramos."""
        season = "Verão" if cls.is_summer(time) else "Inverno"
        weekday = 0 if time.weekday() < 5 or hasattr(cls, 'diario') else time.weekday()
        
        for periodo_horario in cls.PERIODOS[season][weekday]:
            for start, stop in cls.PERIODOS[season][weekday][periodo_horario]:
                if cls.in_time_range(start.hour, start.minute, time, stop.hour, stop.minute):
                    return periodo_horario

    @classmethod
    def get_intervalo_periodo_horario(cls, dt):
        """Retorna o intervalo do periodo horário em que nos encontramos."""
        
        season = "Verão" if cls.is_summer(dt) else "Inverno"
        weekday = 0 if dt.weekday() < 5 or hasattr(cls, 'diario') else dt.weekday()
        
        for tariff in cls.PERIODOS[season][weekday]:
            for start, stop in cls.PERIODOS[season][weekday][tariff]:
                if cls.in_time_range(start.hour, start.minute, dt, stop.hour, stop.minute):
                    start = datetime.combine(dt, start)
                    stop = datetime.combine(dt, stop)
                    start = start.replace(tzinfo=dt.tzinfo)
                    stop = stop.replace(tzinfo=dt.tzinfo)
                    if stop.hour == 0:
                        # Se o intervalo acabar à meia noite, adiciona um dia
                        stop += timedelta(days=1)

                    return (start, stop)

        raise CicloException(f"Não foi possível determinar o intervalo do periodo horário para a data {dt}.")

    @classmethod
    def iter_intervalo_periodo_horario(cls, dt):
        """Retorna o intervalo do próximo periodo horário."""
        while True:
            start, stop = cls.get_intervalo_periodo_horario(dt)
            yield start, stop
            dt = stop + timedelta(minutes=1)


class Ciclo_Semanal(Ciclo):
    """Ciclo semanal continente (os períodos horários diferem entre dias úteis e fim de semana)."""

    def __str__(self) -> str:
        return "Ciclo Semanal"

    PERIODOS = {
        "Verão": {
            0: {
                ph.PONTA: [
                    (time(9, 15), time(12, 15)),
                ],
                ph.CHEIAS: [
                    (time(7, 0), time(9, 15)),
                    (time(12, 15), time(0, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(6, 0), time(7, 0)),
                    (time(0, 0), time(2, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Segunda
            5: {
                ph.CHEIAS: [
                    (time(9, 0), time(14, 0)),
                    (time(20, 0), time(22, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 0)),
                    (time(14, 0), time(20, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Sábado
            6: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Domingo
        },
        "Inverno": {
            0: {
                ph.PONTA: [
                    (time(9, 30), time(12, 00)),
                    (time(18, 30), time(21, 0)),
                ],
                ph.CHEIAS: [
                    (time(7, 0), time(9, 30)),
                    (time(12, 0), time(18, 30)),
                    (time(21, 0), time(0, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(6, 0), time(7, 0)),
                    (time(0, 0), time(2, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Segunda
            5: {
                ph.CHEIAS: [
                    (time(9, 30), time(13, 0)),
                    (time(18, 30), time(22, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 30)),
                    (time(13, 0), time(18, 30)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Sábado
            6: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }, # Domingo
        },
    }



class Ciclo_Diario(Ciclo):
    """Ciclo diário continente (os períodos horários são iguais em todos os dias do ano) """

    diario = True

    def __str__(self) -> str:
        return "Ciclo Diário"
    
    PERIODOS = {
        "Verão": {
            0: {
                ph.PONTA: [
                    (time(10, 30), time(13, 00)),
                    (time(19, 30), time(21, 0)),
                ],
                ph.CHEIAS: [
                    (time(8, 0), time(10, 30)),
                    (time(13, 0), time(19, 30)),
                    (time(21, 0), time(22, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }   # Todos os dias da semana
        },
        "Inverno": {
            0: {
                ph.PONTA: [
                    (time(9, 0), time(10, 30)),
                    (time(18, 0), time(20, 30)),
                ],
                ph.CHEIAS: [
                    (time(8, 0), time(9, 0)),
                    (time(10, 30), time(18, 0)),
                    (time(20, 30), time(22, 0)),
                ],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            }   # Todos os dias da semana
        },
    }





MAPPING = {str(Ciclo_Semanal()): Ciclo_Semanal, str(Ciclo_Diario()): Ciclo_Diario}
