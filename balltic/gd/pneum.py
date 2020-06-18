from ..overrides import set_module
from ..core.euler import EulerianGrid

__author__ = 'Anthony Byuraev'


@set_module('balltic')
class Pneumatic(EulerianGrid):
    """
    Класс - решение основной задачи внутренней баллистики
        в газодинамической постановке на подвижной сетке по методу Эйлера

    Parameters
    ----------
    initial: dict
        Словарь начальных условий и характеристик АО
    press: float, optional
        Начальное давление в каморе
    L0: float, optional
        Начальная длина запоршневого пространства
    L: float, optional
        Длина ведущей части стола

    Returns
    -------
    solution:
    """
