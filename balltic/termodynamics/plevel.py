"""
plevel.py - модуль отвечает за обоснование уровня максимального давления
"""

__author__ = 'Anthony Byuraev'

__all__ = ['PressureLevel']

import os
import math
import typing

import openpyxl
import numpy as np

from balltic.core.guns import ArtilleryGun


class PressureLevel(object):
    """
    Рассчитывает уровень максимального давления на основе аналогов АО
    ---

    Parameters:
        gun: ArtilleryGun
            Именованный кортеж начальных условий и параметров АО
        velocity: int, float
            Требуемая дульная скорость снаряда

    Returns:
        Решение в виде экземпляра класса
    """
    def __init__(self,
                 gun: ArtilleryGun,
                 velocity: typing.Union[int, float]) -> None:
        self.C_Q15 = 15
        self.G = 9.80665
        if isinstance(gun, ArtilleryGun):
            self.gun = gun
        else:
            raise ValueError('Параметр gun должен быть ArtilleryGun')
        if isinstance(velocity, (int, float)):
            self.velocity = velocity
        else:
            raise ValueError('Параметр velocity должен быть int или float')
        self._solve()

    def _load_chuev(self):
        file = os.getcwd() + r'\balltic\termodynamics\chuev.npz'
        table = np.load(file)
        self.table_ce = table['ce']
        self.table_kresherp = table['kresherp']
        self.table_etaomega = table['etaomega']

    def _solve(self):
        self._load_chuev()
        self.ce = self.gun.shell * 1e-3 * self.velocity ** 2 \
            / 2 / self.G / (self.gun.caliber * 10) ** 3
        self.cq = self.gun.shell / (self.gun.caliber * 10) ** 3
        self.etaomega_ce = np.interp(
            self.ce, self.table_ce, self.table_etaomega
        )
        self.ce15 = 0.5 * self.C_Q15 / self.cq * \
            (
                - (3 * self.etaomega_ce * self.cq - self.ce)
                + math.sqrt(
                    (3 * self.etaomega_ce * self.cq - self.ce) ** 2
                    + 12 * self.etaomega_ce * self.ce * (self.cq ** 2) / self.C_Q15
                    )
            )
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
            * (self.gun.K + self.ce15 / self.cq / self.etaomega_ce15 / 3) \
            / (self.gun.fi_1 + self.ce15 / self.cq / self.etaomega_ce15 / 2) \
            * self.G * 1e4
        return self

    def to_excel(self) -> None:
        workbook = openpyxl.Workbook()
        worksheet = workbook.create_sheet('Уровень максимального давления', 0)

        worksheet['A1'] = 'C_q, кг/дм3'
        worksheet['B1'] = self.cq
        worksheet['A2'] = 'C_e, тм/дм3'
        worksheet['B2'] = self.ce
        worksheet['A3'] = 'ETA_omega, тм/кг'
        worksheet['B3'] = self.etaomega_ce
        worksheet['A4'] = 'C_e15, тм/дм3'
        worksheet['B4'] = self.ce15

        # TODO: дописать три оставшихся столбца
        # worksheet['C1'] = 'C_q, кг/дм3'
        # worksheet['D1'] = self.cq
        # worksheet['C2'] = 'C_e, тм/дм3'
        # worksheet['D2'] = self.ce
        # worksheet['C3'] = 'ETA_omega, тм/кг'
        # worksheet['D3'] = self.etaomega_ce
        # worksheet['C4'] = 'C_e15, тм/дм3'
        # worksheet['D4'] = self.ce15

        workbook.save('Pressure_level.xlsx')
        return None
