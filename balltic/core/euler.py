import os

import numpy as np

from ..config import DEFAULT

__author__ = 'Anthony Byuraev'

__all__ = ['EulerianGrid']


class EulerianGrid(object):
    """
    Класс - каркас для построения решений Pneumatic и Gunpowder
    """

    def __str__(self):
        return 'Обьект класса EulerianGrid'

    def __init__(self, initial, nodes=100, press=None, L0=None, L=None):
        self.default = DEFAULT
        self.is_default = False
        self.is_solved = False

        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = initial.get('nodes', self.default['nodes'])
        if press is not None:
            self.press = press
        else:
            self.press = initial.get('press', self.default['press'])

        self.ro = initial.get('ro', self.default['ro'])
        self.kurant = initial.get('Ku', self.default['Ku'])
        self.shell_mass = initial.get('shell_mass', self.default['shell_mass'])
        self.tau = 0

        # длина ячейки на пред. шаге (коор-та 1 границы)
        #   необходимо для расчета веторов q
        self.x_prev = 0
        self.S = np.pi * initial.get('d', self.default['d']) ** 2 / 4

        if L0 is not None:
            self.L0 = L0
        else:
            self.L0 = initial.get('L0', self.default['L0'])
        if L is not None:
            self.L = L
        else:
            self.L = initial.get('L', self.default['L'])

        # параметры газа
        self.R = initial.get('R', self.default['R'])
        self.k = initial.get('k', self.default['k'])

        self.energy_cell = np.full(self.nodes,
                                   self.press / (self.k - 1) / self.ro)
        self.c_cell = np.full(self.nodes,
                              np.sqrt(self.k * self.press / self.ro))
        self.ro_cell = np.full(self.nodes, self.ro)
        self.v_cell = np.zeros(self.nodes)
        self.press_cell = np.zeros(self.nodes)

        # Для расчета Маха на интерфейсе
        self.mah_cell_m = np.zeros(self.nodes - 1)
        self.mah_cell_p = np.zeros(self.nodes - 1)

        # Для расчета потока f (Векторы Ф)
        self.F_param_p = np.array([np.zeros(self.nodes - 1),
                                   np.zeros(self.nodes - 1),
                                   np.zeros(self.nodes - 1)])
        self.F_param_m = np.array([np.zeros(self.nodes - 1),
                                   np.zeros(self.nodes - 1),
                                   np.zeros(self.nodes - 1)])

        self.c_interface = np.zeros(self.nodes - 1)
        self.mah_interface = np.zeros(self.nodes - 1)
        self.press_interface = np.zeros(self.nodes - 1)
        self.v_interface = np.zeros(self.nodes - 1)
        self.x_interface = np.zeros(self.nodes - 1)

        self.f_param = np.array([np.zeros(self.nodes - 1),
                                 self.press_cell[1:],
                                 np.zeros(self.nodes - 1)])
        self.q_param = np.array([self.ro_cell,
                                 self.ro_cell * self.v_cell,
                                 self.ro_cell * (self.energy_cell
                                                 + self.v_cell ** 2 / 2)])
        return self.run()

    def _get_q(self):
        coef_stretch = self.x_prev / self.x_interface[1]

        self.q_param[0][1:-1] = coef_stretch \
            * (self.q_param[0][1:-1]
               - self.tau / self.x_prev
               * (self.f_param[0][1:] - self.f_param[0][:-1]))

        self.q_param[1][1:-1] = coef_stretch \
            * (self.q_param[1][1:-1]
               - self.tau / self.x_prev
               * (self.f_param[1][1:] - self.f_param[1][:-1]))

        self.q_param[2][1:-1] = coef_stretch \
            * (self.q_param[2][1:-1]
               - self.tau / self.x_prev
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
        self.F_param_m[2] = self.ro_cell[:-1] \
            * (self.energy_cell[:-1]
               + self.v_cell[:-1] ** 2 / 2
               + self.press_cell[:-1] / self.ro_cell[:-1])

    def _get_F_plus(self):
        self.F_param_p[0] = self.ro_cell[1:]
        self.F_param_p[1] = self.ro_cell[1:] * self.v_cell[1:]
        self.F_param_p[2] = self.ro_cell[1:] \
            * (self.energy_cell[1:]
               + self.v_cell[1:] ** 2 / 2
               + self.press_cell[1:] / self.ro_cell[1:])

    def _get_c_interface(self):
        self.c_interface = (self.c_cell[1:] + self.c_cell[:-1]) / 2

    def _get_mah_mp(self):
        self.mah_cell_m = (self.v_cell[:-1] - self.v_interface) \
            / self.c_interface
        self.mah_cell_p = (self.v_cell[1:] - self.v_interface) \
            / self.c_interface

    def _get_mah_press_interface(self):
        self.mah_interface = self._fetta_plus() + self._fetta_mines()
        self.press_interface = self._getta_plus() * self.press_cell[:-1] + \
            self._getta_mines() * self.press_cell[1:]

    def _get_tau(self):
        buf = (self.x_interface[1:] - self.x_interface[:-1]) / \
            (abs(self.v_cell[1:-1]) + self.c_cell[1:-1])
        self.tau = self.kurant * min(buf)

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

    def _new_x_interf(self, bottomX):
        """
        Метод определяет новые координаты границ

        Parameters
        ---
        bottomX: float
            Координата последней границы
        """
        self.x_interface = np.linspace(0, bottomX, self.nodes - 1)

    def _end_vel_x(self):
        """
        Функция возвращает список:
            [0] скорость последней границы; [1] коор-та последней границы
        """
        acce = self.press_cell[-2] * self.S / self.shell_mass
        speed = self.v_interface[-1] + acce * self.tau
        x = self.x_interface[-1] \
            + self.v_interface[-1] * self.tau + acce * self.tau ** 2 / 2
        return [speed, x]

    def _fetta_plus(self):
        """
        Параметр в пересчете давления на границе для индекса +
        """
        answer = np.zeros_like(self.mah_cell_m)
        if_cond = np.abs(self.mah_cell_m) >= 1
        else_cond = np.abs(self.mah_cell_m) < 1

        answer[if_cond] = 0.5 * (self.mah_cell_m[if_cond]
                                 + np.abs(self.mah_cell_m[if_cond]))

        answer[else_cond] = 0.25 * (self.mah_cell_m[else_cond] + 1) ** 2 \
                                 * (1 + 4 * 1 / 8 * (self.mah_cell_m[else_cond] - 1) ** 2)
        return answer

    def _fetta_mines(self):
        """
        Параметр в пересчете давления на границе для индекса -
        """
        answer = np.zeros_like(self.mah_cell_p)
        if_cond = np.abs(self.mah_cell_p) >= 1
        else_cond = np.abs(self.mah_cell_p) < 1

        answer[if_cond] = 0.5 * (self.mah_cell_p[if_cond]
                                 - np.abs(self.mah_cell_p[if_cond]))

        answer[else_cond] = -0.25 * (self.mah_cell_p[else_cond] - 1) ** 2 \
                                  * (1 + 4 * 1 / 8 * (self.mah_cell_p[else_cond] + 1) ** 2)
        return answer

    def _getta_plus(self):
        """
        Параметр в пересчете давления на границе для индекса +
        """
        answer = np.zeros_like(self.mah_cell_m)
        if_cond = np.abs(self.mah_cell_m) >= 1
        else_cond = np.abs(self.mah_cell_m) < 1

        answer[if_cond] = (self.mah_cell_m[if_cond]
                           + np.abs(self.mah_cell_m[if_cond])) / 2 / self.mah_cell_m[if_cond]

        answer[else_cond] = (self.mah_cell_m[else_cond] + 1) ** 2 \
            * ((2 - self.mah_cell_m[else_cond]) / 4
                + 3 / 16 * self.mah_cell_m[else_cond]
                * (self.mah_cell_m[else_cond] - 1) ** 2)
        return answer

    def _getta_mines(self):
        """
        Параметр в пересчете давления на границе для индекса -
        """
        answer = np.zeros_like(self.mah_cell_p)
        if_cond = np.abs(self.mah_cell_p) >= 1
        else_cond = np.abs(self.mah_cell_p) < 1

        answer[if_cond] = (self.mah_cell_p[if_cond]
                           - np.abs(self.mah_cell_p[if_cond])) / 2 / self.mah_cell_p[if_cond]

        answer[else_cond] = (self.mah_cell_p[else_cond] - 1) ** 2 \
            * ((2 + self.mah_cell_p[else_cond]) / 4 - 3 / 16 * self.mah_cell_p[else_cond]
                                                             * (self.mah_cell_p[else_cond] + 1) ** 2)
        return answer

    def run(self):
        """
        Решение задачи. Последовательное интегрирование параметров системы
        """

        # Вычисление координат границ в начальный момент времени
        self._new_x_interf(self.L0)

        # Формирование массивов результатов
        self.shell_position = []
        self.shell_velocity = []
        self.shell_pressure = []
        self.stem_pressure = []
        self.time = []

        # Последовательное вычисления с шагом по времени
        while True:
            self._get_tau()
            self.x_prev = self.x_interface[1]
            self._new_x_interf(self._end_vel_x()[1])
            self.v_interface[-1] = self._end_vel_x()[0]
            # линейное распределение скорости
            self.v_interface = (self.v_interface[-1] / self.x_interface[-1]) \
                * self.x_interface

            # заполнение массивов для графиков
            if len(self.time) == 0:
                self.time.append(self.tau)
            else:
                self.time.append(self.tau + self.time[-1])
            self.shell_position.append(self.x_interface[-1])
            self.shell_velocity.append(self.v_interface[-1])
            self.shell_pressure.append(self.press_cell[-2])
            self.stem_pressure.append(self.press_cell[1])

            # последовательные вычисления
            self._get_c_interface()
            self._get_mah_mp()
            self._get_mah_press_interface()
            self._get_F_mines()
            self._get_F_plus()
            self._get_f()
            self._get_q()
            if self.x_interface[-1] >= self.L:
                break
        self.is_solved = True

    def save(self, path=r'\balltic\gd\results.npz'):
        """
        Save solution arrays into a single file in uncompressed ``.npz`` format

        Parameters
        ----------
        file: str or file
            Either the filename (string) or an open file (file-like object)
            where the data will be saved. If file is a string or a Path, the
            ``.npz`` extension will be appended to the filename if it is not
            already there.

        Returns
        -------
        None
        """

        file_path = os.getcwd() + path

        if self.is_solved:
            np.savez(file_path,
                     shell_position=self.shell_position,
                     shell_velocity=self.shell_velocity,
                     shell_pressure=self.shell_pressure,
                     stem_pressure=self.stem_pressure)
            return True
        else:
            raise NotSolvedError

    def load(self, path=r'\balltic\gd\results.npz'):
        file_path = os.getcwd() + path

        try:
            results = np.load(file_path)
        except FileNotFoundError:
            print('FileNotFoundError: Файл не найден или не существует')
            return False

        self.shell_position = results['shell_position']
        self.shell_velocity = results['shell_velocity']
        self.shell_pressure = results['shell_pressure']
        self.stem_pressure = results['stem_pressure']

        return True


class NotSolvedError(Exception):
    def __init__(self):
        super(NotSolvedError, self).__init__('Решение задачи отсутствует')
