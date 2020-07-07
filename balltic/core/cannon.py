__author__ = 'Anthony Byuraev'

import os
import typing
from abc import ABCMeta


BASE_PATH = os.getcwd()
CANNON_KEYS = ()


class BaseGun(metaclass=ABCMeta):
    """
    Реализация артиллерийского орудия
    """


class ArtilleryGun(BaseGun):
    """
    Реализация артиллерийского орудия, стреляющего за счет энергии пороха
    """
    def __init__(self):
        pass


class AirGun(BaseGun):
    """
    Реализация артиллерийского орудия, стреляющего за счет энергии сжатого газа
    """
    def __init__(self):
        pass
