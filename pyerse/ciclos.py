""""Helper com ciclos"""

from datetime import date, time, datetime, timedelta

from pyerse.periodos_horarios import Periodos_Horarios as ph


class Ciclo:
    """Estão previstos dois ciclos: ciclo diário (os períodos horários são iguais em todos os dias do ano) e ciclo semanal (os períodos horários diferem entre dias úteis e fim de semana)."""

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
        # Hora legal de Verão começa no 1º Domingo de Março e acaba no ultimo de Outubro
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
        """Retorna o Periodo Horario em que nos encontramos"""
        raise NotImplementedError


class Ciclo_Semanal(Ciclo):
    """Ciclo semanal continente (os períodos horários diferem entre dias úteis e fim de semana)."""

    def __str__(self) -> str:
        return "Ciclo Semanal"

    @classmethod
    def get_periodo_horario(cls, time):
        if cls.is_summer(time):
            # Verão
            if 0 <= time.weekday() < 5:
                # Seg a Sex
                if cls.in_time_range(9, 15, time, 12, 15):
                    return ph.PONTA
                if cls.in_time_range(7, 0, time, 9, 15) or cls.in_time_range(
                    12, 15, time, 0, 0
                ):
                    return ph.CHEIAS
                if cls.in_time_range(0, 0, time, 2, 0) or cls.in_time_range(
                    6, 0, time, 7, 0
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO
            if time.weekday() == 5:
                # Sabado
                if cls.in_time_range(9, 0, time, 14, 0) or cls.in_time_range(
                    20, 0, time, 22, 0
                ):
                    return ph.CHEIAS
                if (
                    cls.in_time_range(0, 0, time, 2, 0)
                    or cls.in_time_range(6, 0, time, 9, 0)
                    or cls.in_time_range(14, 0, time, 20, 0)
                    or cls.in_time_range(22, 0, time, 0, 0)
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO
            if time.weekday() == 6:
                # Domingo
                if cls.in_time_range(0, 0, time, 2, 0) or cls.in_time_range(
                    6, 0, time, 0, 0
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO
        else:
            # Inverno
            if 0 <= time.weekday() < 5:
                # Seg a Sex
                if cls.in_time_range(9, 30, time, 12, 00) or cls.in_time_range(
                    18, 30, time, 21, 0
                ):
                    return ph.PONTA
                if (
                    cls.in_time_range(7, 0, time, 9, 30)
                    or cls.in_time_range(12, 0, time, 18, 30)
                    or cls.in_time_range(21, 0, time, 0, 0)
                ):
                    return ph.CHEIAS
                if cls.in_time_range(0, 0, time, 2, 0) or cls.in_time_range(
                    6, 0, time, 7, 0
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO
            if time.weekday() == 5:
                # Sabado
                if cls.in_time_range(9, 30, time, 13, 0) or cls.in_time_range(
                    18, 30, time, 22, 0
                ):
                    return ph.CHEIAS
                if (
                    cls.in_time_range(0, 0, time, 2, 0)
                    or cls.in_time_range(6, 0, time, 9, 30)
                    or cls.in_time_range(13, 0, time, 18, 30)
                    or cls.in_time_range(22, 0, time, 0, 0)
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO
            if time.weekday() == 6:
                # Domingo
                if cls.in_time_range(0, 0, time, 2, 0) or cls.in_time_range(
                    6, 0, time, 0, 0
                ):
                    return ph.VAZIO_NORMAL
                if cls.in_time_range(2, 0, time, 6, 0):
                    return ph.SUPER_VAZIO


class Ciclo_Diario(Ciclo):
    """Ciclo diário continente (os períodos horários são iguais em todos os dias do ano) """

    def __str__(self) -> str:
        return "Ciclo Diário"

    @classmethod
    def get_periodo_horario(cls, time):
        if cls.is_summer(time):
            # Verão
            if cls.in_time_range(10, 30, time, 13, 00) or cls.in_time_range(
                19, 30, time, 21, 0
            ):
                return ph.PONTA
            if (
                cls.in_time_range(8, 0, time, 10, 30)
                or cls.in_time_range(13, 0, time, 19, 30)
                or cls.in_time_range(21, 0, time, 22, 0)
            ):
                return ph.CHEIAS
            if (
                cls.in_time_range(6, 0, time, 8, 0)
                or cls.in_time_range(22, 0, time, 0, 0)
                or cls.in_time_range(0, 0, time, 2, 0)
            ):
                return ph.VAZIO_NORMAL
            if cls.in_time_range(2, 0, time, 6, 0):
                return ph.SUPER_VAZIO
        else:
            # Inverno
            if cls.in_time_range(9, 0, time, 10, 30) or cls.in_time_range(
                18, 0, time, 20, 30
            ):
                return ph.PONTA
            if (
                cls.in_time_range(8, 0, time, 9, 0)
                or cls.in_time_range(10, 30, time, 18, 0)
                or cls.in_time_range(20, 30, time, 22, 0)
            ):
                return ph.CHEIAS
            if (
                cls.in_time_range(6, 0, time, 8, 0)
                or cls.in_time_range(22, 0, time, 0, 0)
                or cls.in_time_range(0, 0, time, 2, 0)
            ):
                return ph.VAZIO_NORMAL
            if cls.in_time_range(2, 0, time, 6, 0):
                return ph.SUPER_VAZIO


MAPPING = {str(Ciclo_Semanal()): Ciclo_Semanal, str(Ciclo_Diario()): Ciclo_Diario}
