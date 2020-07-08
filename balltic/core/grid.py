__author__ = 'Anthony Byuraev'

__all__ = ['EulerianGrid', 'BaseGrid']

import os
import typing
from abc import ABCMeta, abstractmethod

import numpy as np

from balltic.core.guns import ArtilleryGun, AirGun
from balltic.core.gpowder import GunPowder


class BaseGrid(metaclass=ABCMeta):
    gun:        typing.Union[ArtilleryGun, AirGun]
    gpowder:    GunPowder
    nodes:      int

    @abstractmethod
    def _get_q(self):
        pass

    @abstractmethod
    def _get_f(self):
        pass

    @abstractmethod
    def _get_F_mines(self):
        pass

    @abstractmethod
    def _get_F_plus(self):
        pass

    @abstractmethod
    def _border(self):
        pass

    @abstractmethod
    def _end_vel_x(self):
        pass

    @abstractmethod
    def _get_c_interface(self):
        pass

    @abstractmethod
    def _get_mah_mp(self):
        pass

    @abstractmethod
    def _get_mah_press_interface(self):
        pass

    @abstractmethod
    def _get_tau(self):
        pass

    @abstractmethod
    def _new_x_interfaces(self):
        pass

    @abstractmethod
    def _fetta_plus(self):
        pass

    @abstractmethod
    def _fetta_mines(self):
        pass

    @abstractmethod
    def _getta_plus(self):
        pass

    @abstractmethod
    def _getta_mines(self):
        pass

    @abstractmethod
    def _run(self):
        pass


class EulerianGrid(BaseGrid):
    """
    Класс реализует общие методы, для расчетов в газодинамической постановке
    """

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __init__(self):
        self.tau = 0
        # длина ячейки на пред. шаге (коор-та 1 границы)
        #   необходимо для расчета веторов q
        self._x_previous = 0

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
        self.tau = self.gun.kurant * min(buf)

    def _new_x_interfaces(self, last_x_interface):
        self.x_interface = np.linspace(0, last_x_interface, self.nodes - 1)

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

    def _run(self):
        """
        Решение задачи. Последовательное интегрирование параметров системы
        """

        # Вычисление координат границ в начальный момент времени
        self._new_x_interfaces(self.gun.chamber)

        # Формирование массивов результатов
        self.shell_position = []
        self.shell_velocity = []
        self.shell_pressure = []
        self.stem_pressure = []
        self.time = []

        # Последовательное вычисления с шагом по времени
        while True:
            self._get_tau()
            self._x_previous = self.x_interface[1]
            self._new_x_interfaces(self._end_vel_x()[1])
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
            if self.x_interface[-1] >= self.gun.barrel:
                break
        self.is_solved = True

    def save(self, path='\\balltic\\results\\results.npz'):
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
        'True' if succes, else raises NotSolvedError
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

    def load(self, path=r'\\balltic\\results\\results.npz'):
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
