__author__ = 'Anthony Byuraev'

__all__ = ['ArtilleryGun', 'PneumaticGun']

import typing


class ArtilleryGun(typing.NamedTuple):
    """
    Реализация артиллерийского орудия, стреляющего за счет энергии пороха

    K: int or float
        Коэффициент второстепенных работ
    fi_1: int or float
        Еще какой то коэффициент, я просто не помню название
    shell: int or float
        Масса снаряда
    barrel: int or float
        Длина ведущей части ствола
    kurant: int or float
        Число Куранта
    boostp: int or float
        Давление форсирования
    caliber: int or float
        Калибр АО
    denload: int or float
        Плотность заряжания
    omega_q: int or float
        Отношение массы заряда к массе снаряда
    press_vsp: int or float
        Давление вспышки
    """
    K:          typing.Union[int, float]
    shell:      typing.Union[int, float]
    barrel:     typing.Union[int, float]
    kurant:     typing.Union[int, float]
    boostp:     typing.Union[int, float]
    caliber:    typing.Union[int, float]
    denload:    typing.Union[int, float]
    omega_q:    typing.Union[int, float]
    press_vsp:  typing.Union[int, float]
    fi_1:       typing.Union[int, float] = None
    cs_area:    typing.Union[int, float] = None
    chamber:    typing.Union[int, float] = None


class PneumaticGun(typing.NamedTuple):
    """
    Реализация артиллерийского орудия, стреляющего за счет энергии сжатого газа

    shell: int or float
        Масса снаряда
    kurant: int or float
        Число Куранта
    barrel: int or float
        Длина ведущей части ствола
    chamber: int or float
        Длина каморы
    caliber: int or float
        Калибр АО
    initialp: int or float
        Начальное давление в каморе
    """
    shell:      typing.Union[int, float]
    kurant:     typing.Union[int, float]
    barrel:     typing.Union[int, float]
    caliber:    typing.Union[int, float]
    chamber:    typing.Union[int, float]
    initialp:   typing.Union[int, float]
    cs_area:    typing.Union[int, float] = None
