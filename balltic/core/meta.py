__author__ = 'Anthony Byuraev'

from abc import ABCMeta, abstractmethod


class BasicGrid(metaclass=ABCMeta):
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
