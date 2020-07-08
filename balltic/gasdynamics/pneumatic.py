__author__ = 'Anthony Byuraev'

__all__ = ['Pneumatic']

import typing

import numpy as np

from balltic.core.grid import EulerianGrid
from balltic.core.guns import AirGun
from balltic.core.gas import Gas


class Pneumatic(EulerianGrid):
    """
    Класс - решение основной задачи внутренней баллистики
        в газодинамической постановке на подвижной сетке по методу Эйлера

    Parameters
    ----------
    gun: AirGun
        Именованный кортеж начальных условий и параметров АО
    gas: Gas
        Именованный кортеж параметров легкого газа
    nodes: int
        Количество узлов (интерфейсов) сетки
    initialp: float, optional
        Начальное давление в каморе
    chamber: int or float, optional
        Начальная длина запоршневого пространства
    barrel: int or float, optional
        Длина ведущей части стола
    kurant: int or float, optional
        Число Куранта

    Returns
    -------
    solution:
    """
    def __str__(self):
        return 'Обьект класса Pneumatic'

    def __repr__(self):
        return f'{self.__class__.__name__}(gun, gas)'

    def __init__(self, gun: AirGun, gas: Gas, nodes=100,
                 initialp: typing.Union[int, float] = None,
                 chamber: typing.Union[int, float] = None,
                 barrel: typing.Union[int, float] = None,
                 kurant: typing.Union[int, float] = None) -> None:

        if isinstance(gun, AirGun):
            self.gun = gun
        else:
            raise ValueError('Параметр gun должен быть AirGun')
        if isinstance(gas, Gas):
            self.gas = gas
        else:
            raise ValueError('Параметр gas должен быть Gas')

        self.nodes = nodes
        if initialp is not None:
            self.gun = self.gun._replace(initialp=initialp)
        if kurant is not None:
            self.gun = self.gun._replace(kurant=kurant)
        if chamber is not None:
            self.gun = self.gun._replace(chamber=chamber)
        if barrel is not None:
            self.gun = self.gun._replace(barrel=barrel)

        self.gun = self.gun._replace(cs_area=np.pi * self.gun.caliber ** 2 / 4)

        self.energy_cell = np.full(
            self.nodes,
            self.gun.initialp / (self.gas.k - 1) / self.gas.ro
        )
        self.c_cell = np.full(
            self.nodes,
            np.sqrt(self.gas.k * self.gun.initialp / self.gas.ro)
        )
        self.ro_cell = np.full(self.nodes, self.gas.ro)
        self.v_cell = np.zeros(self.nodes)
        self.press_cell = np.zeros(self.nodes)

        # Для расчета Маха на интерфейсе
        self.mah_cell_m = np.zeros(self.nodes - 1)
        self.mah_cell_p = np.zeros(self.nodes - 1)

        # Для расчета потока f (Векторы Ф)
        self.F_param_p = np.array(
            [
                np.zeros(self.nodes - 1),
                np.zeros(self.nodes - 1),
                np.zeros(self.nodes - 1)
            ]
        )
        self.F_param_m = np.array(
            [
                np.zeros(self.nodes - 1),
                np.zeros(self.nodes - 1),
                np.zeros(self.nodes - 1)
            ]
        )

        self.c_interface = np.zeros(self.nodes - 1)
        self.mah_interface = np.zeros(self.nodes - 1)
        self.press_interface = np.zeros(self.nodes - 1)
        self.v_interface = np.zeros(self.nodes - 1)
        self.x_interface = np.zeros(self.nodes - 1)

        self.f_param = np.array(
            [
                np.zeros(self.nodes - 1),
                self.press_cell[1:],
                np.zeros(self.nodes - 1)
            ]
        )
        self.q_param = np.array(
            [
                self.ro_cell,
                self.ro_cell * self.v_cell,
                self.ro_cell * (self.energy_cell + self.v_cell ** 2 / 2)
            ]
        )
        self.is_solved = False
        return self._run()

    def _get_q(self):
        coef_stretch = self._x_previous / self.x_interface[1]

        self.q_param[0][1:-1] = coef_stretch \
            * (self.q_param[0][1:-1]
               - self.tau / self._x_previous
               * (self.f_param[0][1:] - self.f_param[0][:-1]))

        self.q_param[1][1:-1] = coef_stretch \
            * (self.q_param[1][1:-1]
               - self.tau / self._x_previous
               * (self.f_param[1][1:] - self.f_param[1][:-1]))

        self.q_param[2][1:-1] = coef_stretch \
            * (self.q_param[2][1:-1]
               - self.tau / self._x_previous
               * (self.f_param[2][1:] - self.f_param[2][:-1]))

        self.ro_cell = self.q_param[0]
        self.v_cell = self.q_param[1] / self.q_param[0]
        self.energy_cell = self.q_param[2] \
            / self.q_param[0] - self.v_cell ** 2 / 2
        self.press_cell = self.ro_cell * self.energy_cell * (self.gas.k - 1)
        self.c_cell = np.sqrt(self.gas.k * self.press_cell / self.ro_cell)
        self._border()

    def _get_f(self):
        self.f_param[0] = self.c_interface / 2 \
            * (self.mah_interface
               * (self.F_param_p[0] + self.F_param_m[0])
               - abs(self.mah_interface)
               * (self.F_param_p[0] - self.F_param_m[0]))

        self.f_param[1] = self.c_interface / 2 \
            * (self.mah_interface
               * (self.F_param_p[1] + self.F_param_m[1])
               - abs(self.mah_interface)
               * (self.F_param_p[1] - self.F_param_m[1])) \
            + self.press_interface

        self.f_param[2] = self.c_interface / 2 \
            * (self.mah_interface
               * (self.F_param_p[2] + self.F_param_m[2])
               - abs(self.mah_interface)
               * (self.F_param_p[2] - self.F_param_m[2])) \
            + self.press_interface * self.v_interface

    def _get_F_mines(self):
        self.F_param_m[0] = self.ro_cell[:-1]
        self.F_param_m[1] = self.ro_cell[:-1] * self.v_cell[:-1]
        self.F_param_m[2] = self.ro_cell[:-1] * (
            self.energy_cell[:-1]
            + self.v_cell[:-1] ** 2 / 2
            + self.press_cell[:-1] / self.ro_cell[:-1]
        )

    def _get_F_plus(self):
        self.F_param_p[0] = self.ro_cell[1:]
        self.F_param_p[1] = self.ro_cell[1:] * self.v_cell[1:]
        self.F_param_p[2] = self.ro_cell[1:] * (
            self.energy_cell[1:]
            + self.v_cell[1:] ** 2 / 2
            + self.press_cell[1:] / self.ro_cell[1:]
        )

    def _border(self):
        self.q_param[0][0] = self.q_param[0][1]
        self.q_param[0][self.nodes - 1] = self.q_param[0][self.nodes - 2]

        self.v_cell[0] = -self.v_cell[1]
        self.q_param[1][0] = self.ro_cell[0] * self.v_cell[0]
        self.q_param[1][self.nodes - 1] = \
            self.q_param[0][self.nodes - 1] \
            * (2 * self.v_interface[self.nodes - 2]
               - self.v_cell[self.nodes - 2])

        self.q_param[2][0] = self.q_param[2][1]
        self.q_param[2][self.nodes - 1] = self.q_param[2][self.nodes - 2]

    def _end_vel_x(self) -> tuple:
        """
        Возвращает скорость и координату последней границы
        """
        acceleration = self.press_cell[-2] * self.gun.cs_area / self.gun.shell
        velocity = self.v_interface[-1] + acceleration * self.tau
        x = self.x_interface[-1] + self.v_interface[-1] * self.tau \
                                 + acceleration * self.tau ** 2 / 2
        return velocity, x
