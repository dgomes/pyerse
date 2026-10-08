""" "Helper com ciclos"""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

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
        if (hour_start, minute_start) == (hour_stop, minute_stop):
            return True
        if (hour_stop, minute_stop) < (hour_start, minute_start):
            return not (time(hour_stop, minute_stop) <= t.time() < time(hour_start, minute_start))
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
    def local_time(cls, dt):
        """Regional cycles accept aware instants or naive regional clock times."""
        if hasattr(cls, "timezone") and dt.tzinfo is not None:
            return dt.astimezone(ZoneInfo(cls.timezone))
        return dt

    @classmethod
    def season(cls, dt):
        if getattr(cls, "monthly_seasons", False):
            return "Junho a Outubro" if 6 <= dt.month <= 10 else "Novembro a Maio"
        return "Verão" if cls.is_summer(dt) else "Inverno"

    @classmethod
    def get_periodo_horario(cls, time):
        """Retorna o Periodo Horario em que nos encontramos."""
        time = cls.local_time(time)
        season = cls.season(time)
        weekday = 0 if time.weekday() < 5 or hasattr(cls, "diario") else time.weekday()

        for periodo_horario in cls.PERIODOS[season][weekday]:
            for start, stop in cls.PERIODOS[season][weekday][periodo_horario]:
                if cls.in_time_range(start.hour, start.minute, time, stop.hour, stop.minute):
                    return periodo_horario

    @classmethod
    def get_intervalo_periodo_horario(cls, dt):
        """Retorna o intervalo do periodo horário em que nos encontramos."""

        dt = cls.local_time(dt)
        season = cls.season(dt)
        weekday = 0 if dt.weekday() < 5 or hasattr(cls, "diario") else dt.weekday()

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

        raise CicloException(
            f"Não foi possível determinar o intervalo do periodo horário para a data {dt}."
        )

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
            },  # Segunda
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
            },  # Sábado
            6: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            },  # Domingo
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
            },  # Segunda
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
            },  # Sábado
            6: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(0, 0)),
                ],
                ph.SUPER_VAZIO: [
                    (time(2, 0), time(6, 0)),
                ],
            },  # Domingo
        },
    }


class Ciclo_Diario(Ciclo):
    """Ciclo diário continente (os períodos horários são iguais em todos os dias do ano)"""

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
            }  # Todos os dias da semana
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
            }  # Todos os dias da semana
        },
    }


class Ciclo_Diario_Acores(Ciclo):
    """Ciclo diário dos Açores, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Azores"
    diario = True

    def __str__(self):
        return "Ciclo Diário Açores"

    PERIODOS = {
        "Verão": {
            0: {
                ph.SUPER_VAZIO: [(time(1, 30), time(5, 30))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(1, 30)),
                    (time(5, 30), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(8, 0), time(9, 0)),
                    (time(11, 30), time(19, 30)),
                    (time(21, 0), time(22, 0)),
                ],
                ph.PONTA: [(time(9, 0), time(11, 30)), (time(19, 30), time(21, 0))],
            },
        },
        "Inverno": {
            0: {
                ph.SUPER_VAZIO: [(time(1, 30), time(5, 30))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(1, 30)),
                    (time(5, 30), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(8, 0), time(9, 30)),
                    (time(11, 0), time(17, 30)),
                    (time(20, 0), time(22, 0)),
                ],
                ph.PONTA: [(time(9, 30), time(11, 0)), (time(17, 30), time(20, 0))],
            },
        },
    }


class Ciclo_Diario_Opcional_Acores(Ciclo):
    """Ciclo diário opcional dos Açores, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Azores"
    diario = True

    def __str__(self):
        return "Ciclo Diário Opcional Açores"

    PERIODOS = {
        "Verão": {
            0: {
                ph.SUPER_VAZIO: [(time(1, 30), time(5, 30))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(1, 30)),
                    (time(5, 30), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(8, 0), time(9, 0)),
                    (time(11, 30), time(19, 30)),
                    (time(21, 0), time(22, 0)),
                ],
                ph.PONTA: [(time(9, 0), time(11, 30)), (time(19, 30), time(21, 0))],
            },
        },
        "Inverno": {
            0: {
                ph.SUPER_VAZIO: [(time(1, 30), time(5, 30))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(1, 30)),
                    (time(5, 30), time(8, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.CHEIAS: [(time(8, 0), time(17, 0)), (time(21, 0), time(22, 0))],
                ph.PONTA: [(time(17, 0), time(21, 0))],
            },
        },
    }


class Ciclo_Semanal_Acores(Ciclo):
    """Ciclo semanal dos Açores, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Azores"
    monthly_seasons = True

    def __str__(self):
        return "Ciclo Semanal Açores"

    PERIODOS = {
        "Junho a Outubro": {
            0: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(7, 0))],
                ph.CHEIAS: [(time(7, 0), time(10, 30)), (time(15, 30), time(0, 0))],
                ph.PONTA: [(time(10, 30), time(15, 30))],
            },
            5: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(11, 0)),
                    (time(14, 30), time(19, 30)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [(time(11, 0), time(14, 30)), (time(19, 30), time(23, 0))],
            },
            6: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(0, 0))],
            },
        },
        "Novembro a Maio": {
            0: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(7, 0))],
                ph.CHEIAS: [(time(7, 0), time(18, 30)), (time(21, 30), time(0, 0))],
                ph.PONTA: [(time(18, 30), time(21, 30))],
            },
            5: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(11, 30)),
                    (time(13, 30), time(18, 0)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [(time(11, 30), time(13, 30)), (time(18, 0), time(23, 0))],
            },
            6: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(0, 0))],
            },
        },
    }


class Ciclo_Diario_Madeira(Ciclo):
    """Ciclo diário dos Madeira, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Madeira"
    diario = True

    def __str__(self):
        return "Ciclo Diário Madeira"

    PERIODOS = {
        "Verão": {
            0: {
                ph.SUPER_VAZIO: [(time(2, 0), time(6, 0))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 0)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(9, 0), time(10, 30)),
                    (time(13, 0), time(20, 30)),
                    (time(22, 0), time(23, 0)),
                ],
                ph.PONTA: [(time(10, 30), time(13, 0)), (time(20, 30), time(22, 0))],
            },
        },
        "Inverno": {
            0: {
                ph.SUPER_VAZIO: [(time(2, 0), time(6, 0))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 0)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(9, 0), time(10, 30)),
                    (time(12, 0), time(18, 30)),
                    (time(21, 0), time(23, 0)),
                ],
                ph.PONTA: [(time(10, 30), time(12, 0)), (time(18, 30), time(21, 0))],
            },
        },
    }


class Ciclo_Diario_Opcional_Madeira(Ciclo):
    """Ciclo diário opcional dos Madeira, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Madeira"
    diario = True

    def __str__(self):
        return "Ciclo Diário Opcional Madeira"

    PERIODOS = {
        "Verão": {
            0: {
                ph.SUPER_VAZIO: [(time(2, 0), time(6, 0))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 0)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [
                    (time(9, 0), time(10, 30)),
                    (time(13, 0), time(20, 30)),
                    (time(22, 0), time(23, 0)),
                ],
                ph.PONTA: [(time(10, 30), time(13, 0)), (time(20, 30), time(22, 0))],
            },
        },
        "Inverno": {
            0: {
                ph.SUPER_VAZIO: [(time(2, 0), time(6, 0))],
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(2, 0)),
                    (time(6, 0), time(9, 0)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [(time(9, 0), time(18, 0)), (time(22, 0), time(23, 0))],
                ph.PONTA: [(time(18, 0), time(22, 0))],
            },
        },
    }


class Ciclo_Semanal_Madeira(Ciclo):
    """Ciclo semanal dos Madeira, segundo os horários ERSE de 2026."""

    timezone = "Atlantic/Madeira"
    monthly_seasons = True

    def __str__(self):
        return "Ciclo Semanal Madeira"

    PERIODOS = {
        "Junho a Outubro": {
            0: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(7, 0))],
                ph.CHEIAS: [
                    (time(7, 0), time(11, 0)),
                    (time(14, 0), time(20, 0)),
                    (time(22, 0), time(0, 0)),
                ],
                ph.PONTA: [(time(11, 0), time(14, 0)), (time(20, 0), time(22, 0))],
            },
            5: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(11, 0)),
                    (time(14, 30), time(19, 30)),
                    (time(23, 0), time(0, 0)),
                ],
                ph.CHEIAS: [(time(11, 0), time(14, 30)), (time(19, 30), time(23, 0))],
            },
            6: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(0, 0))],
            },
        },
        "Novembro a Maio": {
            0: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(7, 0))],
                ph.CHEIAS: [(time(7, 0), time(19, 0)), (time(22, 0), time(0, 0))],
                ph.PONTA: [(time(19, 0), time(22, 0))],
            },
            5: {
                ph.VAZIO_NORMAL: [
                    (time(0, 0), time(11, 30)),
                    (time(14, 0), time(18, 0)),
                    (time(22, 30), time(0, 0)),
                ],
                ph.CHEIAS: [(time(11, 30), time(14, 0)), (time(18, 0), time(22, 30))],
            },
            6: {
                ph.VAZIO_NORMAL: [(time(0, 0), time(0, 0))],
            },
        },
    }


MAPPING = {
    str(cycle()): cycle
    for cycle in (
        Ciclo_Semanal,
        Ciclo_Diario,
        Ciclo_Diario_Acores,
        Ciclo_Diario_Opcional_Acores,
        Ciclo_Semanal_Acores,
        Ciclo_Diario_Madeira,
        Ciclo_Diario_Opcional_Madeira,
        Ciclo_Semanal_Madeira,
    )
}
