import numpy as np

from balltic.core.euler import EulerianGrid
from ..config import PNEUMATIC_CANNON

__author__ = 'Anthony Byuraev'


class Pneumatic(EulerianGrid):
    """
    Класс - решение основной задачи внутренней баллистики
        в газодинамической постановке на подвижной сетке по методу Эйлера

    Parameters
    ----------
    cannon: dict
        Словарь начальных условий и характеристик АО
    nodes: int, optional
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

    def __init__(self, cannon, nodes=None, initialp=None,
                 chamber=None, barrel=None, kurant=None):
        self.default = PNEUMATIC_CANNON
        self.is_solved = False

        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = cannon.get('nodes', self.default['nodes'])
        if initialp is not None:
            self.press = initialp
        else:
            self.press = cannon.get('initialp', self.default['initialp'])
        if kurant is not None:
            self.kurant = kurant
        else:
            self.kurant = cannon.get('Ku', self.default['Ku'])
        if chamber is not None:
            self.chamber = chamber
        else:
            self.chamber = cannon.get('chamber', self.default['chamber'])
        if barrel is not None:
            self.barrel = barrel
        else:
            self.barrel = cannon.get('barrel', self.default['barrel'])

        self.ro = cannon.get('ro', self.default['ro'])
        self.shell = cannon.get('shell', self.default['shell'])
        self.square = np.pi * cannon.get(
            'caliber', self.default['caliber']) ** 2 / 4

        # параметры газа
        self.R = cannon.get('R', self.default['R'])
        self.k = cannon.get('k', self.default['k'])

        self.energy_cell = np.full(
            self.nodes,
            self.press / (self.k - 1) / self.ro
        )
        self.c_cell = np.full(
            self.nodes,
            np.sqrt(self.k * self.press / self.ro)
        )
        self.ro_cell = np.full(self.nodes, self.ro)
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
        return self._run()

    def _get_q(self):
        coef_stretch = self.x_previous / self.x_interface[1]

        self.q_param[0][1:-1] = coef_stretch \
            * (self.q_param[0][1:-1]
               - self.tau / self.x_previous
               * (self.f_param[0][1:] - self.f_param[0][:-1]))

        self.q_param[1][1:-1] = coef_stretch \
            * (self.q_param[1][1:-1]
               - self.tau / self.x_previous
               * (self.f_param[1][1:] - self.f_param[1][:-1]))

        self.q_param[2][1:-1] = coef_stretch \
            * (self.q_param[2][1:-1]
               - self.tau / self.x_previous
               * (self.f_param[2][1:] - self.f_param[2][:-1]))

        self.ro_cell = self.q_param[0]
        self.v_cell = self.q_param[1] / self.q_param[0]
        self.energy_cell = self.q_param[2] \
            / self.q_param[0] - self.v_cell ** 2 / 2
        self.press_cell = self.ro_cell * self.energy_cell * (self.k - 1)
        self.c_cell = np.sqrt(self.k * self.press_cell / self.ro_cell)
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
        acceleration = self.press_cell[-2] * self.square / self.shell
        velocity = self.v_interface[-1] + acceleration * self.tau
        x = self.x_interface[-1] + self.v_interface[-1] * self.tau \
                                 + acceleration * self.tau ** 2 / 2
        return velocity, x
