"""
mxp.py -- модуль отвечает за обоснование уровня максимального давления
"""

import os
from math import sqrt

import numpy as np

__author__ = 'Anthony Byuraev'


PATH_BASE = os.getcwd()


class MPress(object):
    """
    Рассчитывает уровень максимального давления на основе аналогов АО

    Parameters
    ----------
    cannon: dict
        Словарь начальных условий и характеристик АО
    velocity: int, float
        Требуемая скорость снаряда

    Returns
    -------
    solution:
    """
    def __init__(self, cannon, velocity):
        self.CQ15 = 15
        self.G = 9.80665

        try:
            self.shell = cannon.get('shell')
        except Exception:
            raise FieldNotFoundError('shell')
        try:
            self.caliber = cannon.get('caliber')
        except Exception:
            raise FieldNotFoundError('caliber')
        try:
            self.K = cannon.get('K')
        except Exception:
            raise FieldNotFoundError('K')
        try:
            self.fi_1 = cannon.get('fi_1')
        except Exception:
            raise FieldNotFoundError('fi_1')
        self.velocity = velocity

    def _load_chuev(self, path_to_file: str = r'\balltic\td\chuev.npz'):
        FILE = PATH_BASE + path_to_file
        table = np.load(FILE)

        self.table_ce = table['ce']
        self.table_kresherp = table['kresherp']
        self.table_etaomega = table['etaomega']

    def solve(self):
        self._load_chuev()

        self.ce = self.shell * 1e-3 * self.velocity ** 2 \
            / 2 / self.G / (self.caliber * 10) ** 3
        self.cq = self.shell / (self.caliber * 10) ** 3
        self.etaomega_ce = np.interp(
            self.ce, self.table_ce, self.table_etaomega
        )
        self.ce15 = 0.5 * self.CQ15 / self.cq * \
            (- (3 * self.etaomega_ce * self.cq - self.ce)
             + sqrt((3 * self.etaomega_ce * self.cq - self.ce) ** 2
             + 12 * self.etaomega_ce * self.ce * (self.cq ** 2) / self.CQ15))
        self.etaomega_ce15 = np.interp(
            self.ce15, self.table_ce, self.table_etaomega
        )
        self.kresherp = np.interp(
            self.ce15, self.table_ce, self.table_kresherp
        )
        self.omega_q = self.ce15 / self.cq / self.etaomega_ce15
        self.n_kresher = np.interp(
            self.omega_q, np.array([0.5, 2]), np.array([1.12, 1.23])
        )
        self.maximum = self.kresherp * self.n_kresher \
            * (self.K + self.ce15 / self.cq / self.etaomega_ce15 / 3) \
            / (self.fi_1 + self.ce15 / self.cq / self.etaomega_ce15 / 2) * self.G * 1e4
        return self


class FieldNotFoundError(Exception):
    def __init__(self, field):
        super(FieldNotFoundError, self).__init__(
            'FieldNotFoundError: Параметр {} не найден или отсутствует'.format(field)
        )
