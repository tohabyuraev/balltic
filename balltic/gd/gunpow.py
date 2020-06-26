__author__ = 'Anthony Byuraev'

import numpy as np

from balltic.powders import Powder
from balltic.core.euler import EulerianGrid
from balltic.config import GUNPOWDER_CANNON


class Gunpowder(EulerianGrid):
    """
    Класс - решение основной задачи внутренней баллистики
        в газодинамической постановке на подвижной сетке по методу Эйлера

    Parameters
    ----------
    cannon: dict
        Словарь начальных условий и характеристик АО
    powder: str
        Название пороха
    nodes: int, optional
        Количество узлов (интерфейсов) сетки
    omega_q: int or float, optional
        Отношение массы заряда к массе снаряда
    denload: int or float, optional
        Плотность заряжания
    barrel: int or float, optional
        Длина ведущей части стола
    kurant: int or float, optional
        Число Куранта
    boostp: int or float, optional
        Значение давления форсирования

    Returns
    -------
    solution:
    """
    def __str__(self):
        return 'Обьект класса Gunpowder'

    def __init__(self, cannon, powder, nodes=None, omega_q=None,
                 denload=None, barrel=None, kurant=None, boostp=None):
        self.default_cannon = GUNPOWDER_CANNON
        self.default_powder = None
        self.is_solved = False

        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = cannon.get('nodes', self.default_cannon['nodes'])
        if boostp is not None:
            self.boostp = boostp
        else:
            self.boostp = cannon.get('boostp', self.default_cannon['boostp'])
        if barrel is not None:
            self.barrel = barrel
        else:
            self.barrel = cannon.get('barrel', self.default_cannon['barrel'])
        if kurant is not None:
            self.kurant = kurant
        else:
            self.kurant = cannon.get('kurant', self.default_cannon['kurant'])

        self.shell = cannon.get('shell', self.default_cannon['shell'])
        if omega_q is not None:
            self.omega_q = omega_q
        else:
            self.omega_q = cannon.get(
                'omega_q', self.default_cannon['omega_q'])
        if denload is not None:
            self.ro = denload
        else:
            self.ro = cannon.get(
                'denload', self.default_cannon['denload'])

        self.omega = self.omega_q * self.shell
        self.square = np.pi * cannon['caliber'] ** 2 / 4
        self.powder = Powder(powder)
        self.chamber = self.omega / self.ro / self.square

        self.ro_cell = np.full(self.nodes, self.ro)
        self.v_cell = np.full(self.nodes, 0.0)
        self.zet_cell = np.full(self.nodes, 0.0)
        self.press_cell = np.full(self.nodes, cannon['press_vsp'])
        self.psi_cell = self._psi()
        self.energy_cell = np.full(
            self.nodes,
            self.press_cell / (self.powder.k - 1)
            * (1 / self.ro_cell - (
                (1 - self.psi_cell) / self.powder.ro + self.powder.alpha_k * self.psi_cell))
            + (1 - self.psi_cell) * self.powder.f / (self.powder.k - 1)
        )
        self.c_cell = np.full(
            self.nodes,
            1 / self.ro_cell * np.sqrt(
                self.powder.k * self.press_cell
                / (1 / self.ro_cell - (1 - self.psi_cell) / self.powder.ro - self.powder.alpha_k * self.psi_cell)
            )
        )

        # для расчета Маха на интерфейсе
        self.mah_cell_m = np.full(self.nodes - 1, 0.0)
        self.mah_cell_p = np.full(self.nodes - 1, 0.0)

        # для расчета потока q (Векторы H)
        self.h_param = np.full(
            self.nodes,
            self.ro_cell * self.press_cell / self.powder.I_k
        )

        # для расчета потока f (Векторы Ф )
        self.F_param_p = np.array(
            [
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0)
            ]
        )

        self.F_param_m = np.array(
            [
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0)
            ]
        )

        # для параметров на границах
        self.c_interface = np.full(self.nodes - 1, 0.0)
        self.mah_interface = np.full(self.nodes - 1, 0.0)
        self.press_interface = np.full(self.nodes - 1, 0.0)
        self.v_interface = np.full(self.nodes - 1, 0.0)
        self.x_interface = np.full(self.nodes - 1, 0.0)

        # векторы состояний и потоков
        self.f_param = np.array(
            [
                np.full(self.nodes - 1, 0.0),
                self.press_cell[1:],
                np.full(self.nodes - 1, 0.0),
                np.full(self.nodes - 1, 0.0)
            ]
        )
        self.q_param = np.array(
            [
                self.ro_cell,
                self.ro_cell * self.v_cell,
                self.ro_cell * (self.energy_cell + self.v_cell ** 2 / 2),
                self.ro_cell * self.zet_cell
            ]
        )
        return self._run()

    # TODO: Необходимо разобраться с функцией газоприхода
    # def _psi(self):
    #     """
    #     Функция газоприхода
    #     """
    #     if_cond = self.zet_cell <= 1
    #     elif_cond = self.zet_cell <= self.powder.z_k
    #     else_cond = self.zet_cell > self.powder.z_k

    #     answer = np.zeros_like(self.zet_cell)
    #     answer[if_cond] = self.powder.k_1 \
    #         * self.zet_cell[if_cond] \
    #         * (1 + self.powder.lambda_1 * self.zet_cell[if_cond])
    #     answer[elif_cond] = self.powder.k_2 \
    #         * (self.zet_cell[elif_cond] - 1) \
    #         * (1 + self.powder.lambda_2 * (self.zet_cell[elif_cond] - 1))
    #     answer[else_cond] = np.ones_like(self.zet_cell[else_cond])
    #     return answer

    def _psi(self):
        """
        Функция газоприхода
        """
        buf = []
        for zet in self.zet_cell:
            if (zet <= 1):
                buf.append(self.powder.k_1 * zet * (1 + self.powder.lambda_1 * zet))
            elif (zet <= self.powder.z_k):
                buf.append(self.powder.k_2 * (zet - 1) * (1 + self.powder.lambda_2 * (zet - 1)))
            else:
                buf.append(1.0)
            # else: buf.append(self.k_2 * (self.z_k - 1) * (1 + self.lambda_2 * (self.z_k - 1)))
        return np.asarray(buf)

    def _get_q(self):
        self.h_param = self.ro_cell * self.press_cell / self.powder.I_k
        coef_stretch = self.x_previous / self.x_interface[1]
        self.q_param[0][1:-1] = coef_stretch * (
            self.q_param[0][1:-1]
            - self.tau / self.x_previous
            * (self.f_param[0][1:] - self.f_param[0][:-1])
        )
        self.q_param[1][1:-1] = coef_stretch * (
            self.q_param[1][1:-1]
            - self.tau / self.x_previous
            * (self.f_param[1][1:] - self.f_param[1][:-1])
        )
        self.q_param[2][1:-1] = coef_stretch * (
            self.q_param[2][1:-1]
            - self.tau / self.x_previous
            * (self.f_param[2][1:] - self.f_param[2][:-1])
        )
        self.q_param[3][1:-1] = coef_stretch * (
            self.q_param[3][1:-1]
            - self.tau / self.x_previous
            * (
                self.f_param[3][1:] - self.f_param[3][:-1]
                - self.h_param[1:-1] * self.x_interface[1]
            )
        )

        self.ro_cell = self.q_param[0]
        self.v_cell = self.q_param[1] / self.q_param[0]
        self.energy_cell = self.q_param[2] / self.q_param[0] - self.v_cell ** 2 / 2
        self.zet_cell = self.q_param[3] / self.q_param[0]
        self.psi_cell = self._psi()
        self.press_cell = (self.energy_cell - (1 - self.psi_cell) * self.powder.f / (self.powder.k - 1)) * \
            (self.powder.k - 1) / (1 / self.ro_cell - ((1 - self.psi_cell) / self.powder.ro +
                self.powder.alpha_k * self.psi_cell))
        self.c_cell = 1 / self.ro_cell * np.sqrt(
            self.powder.k * self.press_cell
            / (1 / self.ro_cell - (1 - self.psi_cell) / self.powder.ro - self.powder.alpha_k * self.psi_cell)
        )
        self._border()

    def _get_f(self):
        self.f_param[0] = self.c_interface / 2 * (
            self.mah_interface
            * (self.F_param_p[0] + self.F_param_m[0])
            - abs(self.mah_interface)
            * (self.F_param_p[0] - self.F_param_m[0])
        )
        self.f_param[1] = self.c_interface / 2 * (
            self.mah_interface
            * (self.F_param_p[1] + self.F_param_m[1])
            - abs(self.mah_interface)
            * (self.F_param_p[1] - self.F_param_m[1])
        ) + self.press_interface
        self.f_param[2] = self.c_interface / 2 * (
            self.mah_interface
            * (self.F_param_p[2] + self.F_param_m[2])
            - abs(self.mah_interface)
            * (self.F_param_p[2] - self.F_param_m[2])
        ) + self.press_interface * self.v_interface
        self.f_param[3] = self.c_interface / 2 * (
            self.mah_interface
            * (self.F_param_p[3] + self.F_param_m[3])
            - abs(self.mah_interface)
            * (self.F_param_p[3] - self.F_param_m[3])
        )

    def _get_F_mines(self):
        self.F_param_m[0] = self.ro_cell[:-1]
        self.F_param_m[1] = self.ro_cell[:-1] * self.v_cell[:-1]
        self.F_param_m[2] = self.ro_cell[:-1] * (
            self.energy_cell[:-1]
            + self.v_cell[:-1] ** 2 / 2
            + self.press_cell[:-1] / self.ro_cell[:-1]
        )
        self.F_param_m[3] = self.ro_cell[:-1] * self.zet_cell[:-1]

    def _get_F_plus(self):
        self.F_param_p[0] = self.ro_cell[1:]
        self.F_param_p[1] = self.ro_cell[1:] * self.v_cell[1:]
        self.F_param_p[2] = self.ro_cell[1:] * (
            self.energy_cell[1:]
            + self.v_cell[1:] ** 2 / 2
            + self.press_cell[1:] / self.ro_cell[1:]
        )
        self.F_param_p[3] = self.ro_cell[1:] * self.zet_cell[1:]

    def _border(self):
        """
        Метод "граничных условий"
        Переопределяет значения вектора q в первой и последней ячейке,
            а также скорость газа в первой ячейке,
            чтобы выполнялись граничные условия
        """
        self.q_param[0][0] = self.q_param[0][1]
        self.q_param[0][-1] = self.q_param[0][-2]

        self.v_cell[0] = -self.v_cell[1]
        self.q_param[1][0] = self.ro_cell[0] * self.v_cell[0]
        self.q_param[1][-1] = self.q_param[0][-1] \
            * (2 * self.v_interface[-2] - self.v_cell[-2])

        self.q_param[2][0] = self.q_param[2][1]
        self.q_param[2][-1] = self.q_param[2][-2]

        self.q_param[3][0] = self.q_param[3][1]
        self.q_param[3][-1] = self.q_param[3][-2]

    def _end_vel_x(self):
        """
        Возвращает скорость и координату последней границы
        Если давление не достигает давления форсирования,
            то [0] = 0, [1] = const
        """
        if self.press_cell[-2] < self.boostp:
            return 0, self.x_interface[-1]
        else:
            acceleration = self.press_cell[-2] * self.square / self.shell
            velocity = self.v_interface[-1] + acceleration * self.tau
            x = self.x_interface[-1] + self.v_interface[-1] * self.tau \
                                     + acceleration * self.tau ** 2 / 2
            return velocity, x
