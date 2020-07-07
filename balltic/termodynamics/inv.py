"""
inv.py -- модуль отвечает за решение обратной задачи
    на основе аналитических зависимостей
"""

__author__ = 'Anthony Byuraev'

import numpy as np

from balltic.td.mxp import MaxPressure
from balltic.config import AVERAGE_GP, G_CANNON


PYROPAR_FILE = 'pyropar.xlsx'
ANDEP_FILE = 'andep.xlsx'


class ReverAn(object):
    """
    Решает обратную задачу на основе аналитичеких зависимостей

    Parameters
    ----------
    max_pressure: int, float
        Максимальное требуемое давление в канале ствола
    cannon: dict
        Словарь начальных условий и характеристик АО
    denload: list
        Список плотностей заряжания

    Returns
    -------
    files:
    """
    def __str__(self):
        return 'Обьект класса ReverAn'

    def __repr__(self):
        return (f'{self.__class__.__name__}()')

    def __init__(self, max_pressure, cannon, denload):
        self.cannon = cannon
        self.gpowder = AVERAGE_GP
        self.default_cannon = G_CANNON

        self.drozdov_max = 10
        self.drozdov_min = 0
        self.drozdov = 5

        self.required_level = max_pressure / self.cannon['boostp']

        return None

    @staticmethod
    def max_pressure(cannon, velocity):
        max_pressure = MaxPressure(cannon, velocity).maximum
        return max_pressure

    def _pyro(self):


def reverse_analytics(max_pressure, cannon, denload):

    dParam = []
    a_r_k = []
    a_L_k = []
    a_ksi_1 = []

    for density in denload:
        ksi_1 = 1 - (gpowder['k'] - 1) * (1 - gpowder['coolum']
                * gpowder['density']) / gpowder['density'] * max_press / 2 / gpowder['f']
        psi_0 = (1 / density - 1 / gpowder['density']) / (gpowder['f'] /
                 cannon['boost_press'] - 1 / gpowder['density'] + gpowder['coolum'])
        sigma_0 = sqrt(1 + 4 * gpowder['lambda_1'] / gpowder['kappa_1'] * psi_0)
        z_0 = 2 * psi_0 / gpowder['kappa_1'] / (1 + sigma_0)
        drozdov = 5
        drozdov_max = 10
        drozdov_min = 0
        requiredLevel = max_press / cannon['boost_press']
        cond = True
        while cond:
            c_betta = (gpowder['k'] - 1) / 2 * drozdov / gpowder['kappa_1'] / sigma_0 - \
                      ksi_1 * gpowder['lambda_1'] / sigma_0
            alfa_1 = 2 * gpowder['lambda_1'] / sigma_0 / c_betta
            gamma_1 = psi_0 / gpowder['kappa_1'] / sigma_0 * c_betta
            betta_1 = ksi_1 / 2 + sqrt(ksi_1 ** 2 / 4 + gamma_1)
            betta_2 = ksi_1 / 2 - sqrt(ksi_1 ** 2 / 4 + gamma_1)
            betta_m = (gpowder['k'] * ksi_1 - 1) / (2 * gpowder['k'] + alfa_1)
            fi_bm = (1 - betta_m / betta_2) ** ((1 + alfa_1 * betta_2) / (betta_1 - betta_2) - 1) / \
                (1 - betta_m / betta_1) ** ((1 + alfa_1 * betta_1) / (betta_1 - betta_2) + 1)
            pressure_value = (1 - betta_m / betta_1) * (1 - betta_m / betta_2) * \
                                fi_bm ** (-1 / (gpowder['k'] - 1))
            cond = abs(requiredLevel - pressure_value) < 1e-6
            if cond:
                cond = False
            else:
                # Пересчет параметра Дроздова
                if pressure_value < requiredLevel:
                    drozdov_max = drozdov
                    drozdov = (drozdov_max + drozdov_min) / 2
                else:
                    drozdov_min = drozdov
                    drozdov = (drozdov_max + drozdov_min) / 2
                cond = True
        betta_k = c_betta * (1 - z_0)
        fi_bk = (1 - betta_k / betta_2) ** ((1 + alfa_1 * betta_2) / (betta_1 - betta_2) - 1) / \
            (1 - betta_k / betta_1) ** ((1 + alfa_1 * betta_1) / (betta_1 - betta_2) + 1)
        L_k = gpowder['f'] * density * psi_0 / cannon['boost_press'] * \
            (fi_bk ** (1 / (gpowder['k'] - 1)) - 1) - (1 - gpowder['coolum'] * gpowder['density']) / \
                gpowder['density'] * density * gpowder['kappa_1'] * sigma_0 / \
                    c_betta * (1 + alfa_1 * betta_k / 2) * betta_k
        r_k = (gpowder['k'] - 1) / 2 * drozdov * (1 - z_0) ** 2
        dParam.append(drozdov)
        a_L_k.append(L_k)
        a_r_k.append(r_k)
        a_ksi_1.append(ksi_1)

    with pd.ExcelWriter(PYROPAR_FILE) as writer:
        df = pd.DataFrame(array([denload, dParam, a_r_k, a_L_k, a_ksi_1])).transpose()
        df.to_excel(writer)


def andep(denload, gpowder, cannon):
    df = pd.read_excel(PYROPAR_FILE)
    dParam, rK, lK, ksi1 = asarray(df[1]), asarray(df[2]), asarray(df[3]), asarray(df[4])
    etaK = np.linspace(0.2, 1, 17)
    s = pi * cannon['d'] ** 2 / 4 * 1.04

    res1 = []
    res2 = []
    res3 = []
    res4 = []
    res5 = []
    res6 = []

    st1 = 21
    st2 = 17

    for eta_k in etaK:
        lD = lK / eta_k
        r_d = ksi1 - (ksi1 - rK) \
            * ((1 - gpowder['coolum'] * denload + lK)
               / (1 - gpowder['coolum'] * denload + lD)) ** (gpowder['k'] - 1)
        omega = cannon['K'] * cannon['q'] \
            / (2 * gpowder['f'] * r_d / (gpowder['k'] - 1)
               / cannon['velocity'] ** 2 - 1 / 3)
        W_0 = omega / denload
        l_0 = W_0 / s
        lD = lD * l_0
        I_k = sqrtn(gpowder['f'] * omega * cannon['q'] * dParam *
                    (cannon['K'] + omega / cannon['q'] / 3)) / s
        Z_sl = 1e6 * sqrtn(1 + lD) \
            / ((lD + W_0 / s / 1.35 + 1.5 * cannon['d'])
                / cannon['d']) ** 4 / (omega / cannon['q']) ** (3 / 2)

        res1.append(I_k / 1e6)
        res2.append((W_0 + s * lD) / cannon['d'] ** 3)
        res3.append(lD / cannon['d'])
        res4.append(omega / cannon['q'])
        res5.append(Z_sl)
        res6.append(W_0 / cannon['d'] ** 3)

    res1 = asarray(res1)
    res2 = asarray(res2)
    res3 = asarray(res3)
    res4 = asarray(res4)
    res5 = asarray(res5)
    res6 = asarray(res6)
    df1 = pd.DataFrame(res1.reshape(st2, st1)).transpose()
    df2 = pd.DataFrame(res2.reshape(st2, st1)).transpose()
    df3 = pd.DataFrame(res3.reshape(st2, st1)).transpose()
    df4 = pd.DataFrame(res4.reshape(st2, st1)).transpose()
    df5 = pd.DataFrame(res5.reshape(st2, st1)).transpose()
    df6 = pd.DataFrame(res6.reshape(st2, st1)).transpose()

    with pd.ExcelWriter(ANDEP_FILE) as writer:
        df1.to_excel(writer, sheet_name='I_k')
        df2.to_excel(writer, sheet_name='Wkn_d3')
        df3.to_excel(writer, sheet_name='ld_d')
        df4.to_excel(writer, sheet_name='omega_q')
        df5.to_excel(writer, sheet_name='Zsl')
        df6.to_excel(writer, sheet_name='W0_d3')
