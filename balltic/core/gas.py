__author__ = 'Anthony Byuraev'

__all__ = ['Gas']

import typing


class Gas(typing.NamedTuple):
    """
    Реализация легкого газа для разгона метаемых тел

    k: int or float
        Показатель адиабаты газа
    R: int or float
        Газовая постоянная газа
    ro: int or float
        Плотность газа
    """
    k:          typing.Union[int, float]
    R:          typing.Union[int, float]
    ro:         typing.Union[int, float]
