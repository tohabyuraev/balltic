__author__ = 'Anthony Byuraev'

__all__ = ['GunPowder']

import os
import json
import typing
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractclassmethod
from abc import abstractstaticmethod


BASE_PATH = os.getcwd()
GUNPOWDER_KEYS = (
    'f',
    'ro',
    'k_1',
    'k_2',
    'I_k',
    'Z_k',
    'etta',
    'name',
    'alpha_k',
    'lambda_1',
    'lambda_2',
)


class BasePowder(metaclass=ABCMeta):
    """
    Основа для реализации пороха
    """
    name:       str
    k:          typing.Union[int, float]
    f:          typing.Union[int, float]
    ro:         typing.Union[int, float]
    k_1:        typing.Union[int, float]
    k_2:        typing.Union[int, float]
    I_k:        typing.Union[int, float]
    z_k:        typing.Union[int, float]
    # T_1:      typing.Union[int, float]
    alpha_k:    typing.Union[int, float]
    lambda_1:   typing.Union[int, float]
    lambda_2:   typing.Union[int, float]
    _gpowder:   typing.Dict[str, dict]

    @abstractstaticmethod
    def load_database(self, file_path: typing.IO[str] = None) -> typing.Dict[str, dict]:
        pass

    @abstractclassmethod
    def load_gunpowder(self, name: str) -> dict:
        pass

    @abstractmethod
    def _check_gunpowder(self, gunpowder: dict) -> dict:
        pass


class GunPowder(BasePowder):
    """
    Реализация артиллерийского пороха
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self._gunpowder = self.load_gunpowder(self.name)

        self.k = self._gunpowder['etta'] + 1
        self.f = self._gunpowder['f'] * 1e6
        self.ro = self._gunpowder['ro'] * 1e3
        self.k_1 = self._gunpowder['k_1']
        self.k_2 = self._gunpowder['k_2']
        self.I_k = self._gunpowder['I_k'] * 1e6
        self.z_k = self._gunpowder['Z_k']
        # self.T_1 = self._gunpowder['T_1']
        self.alpha_k = self._gunpowder['alpha_k'] * 1e-3
        self.lambda_1 = self._gunpowder['lambda_1']
        self.lambda_2 = self._gunpowder['lambda_2']

    def __str__(self):
        return str(self._gunpowder)

    def __repr__(self):
        return 'GunPowder("gunpowder_name")'

    def _check_gunpowder(self, gunpowder: dict) -> dict:
        for key in GUNPOWDER_KEYS:
            try:
                gunpowder[key]
            except KeyError:
                raise KeyError('Параметр пороха не существует')
        return gunpowder

    @staticmethod
    def load_database(file_path: typing.IO[str] = None) -> typing.Dict[str, dict]:
        """
        Загружает все пороха из базы данных, расположенной в
            balltic\\powders\\gpowders.json

        Parameters
        ----------
        file_path: TextIO or BinaryIO, optional
            Путь к файлу базы данных
        """
        if file_path is not None:
            file_path = file_path
        else:
            file_path = '\\balltic\\powders\\gpowders.json'
        try:
            with open(BASE_PATH + file_path) as file_:
                return json.load(file_)
        except FileNotFoundError:
            raise FileNotFoundError('Файл не найден или не существует')

    @classmethod
    def load_gunpowder(self, name: str) -> dict:
        """
        Загружает по названию порох из базы данных, расположенной в
            "balltic\\powders\\gpowders.json"

        Parameters
        ----------
        name: str
            Название пороха. Следует писать дробь через двойной обратный слэш
            Пример:
                '16/1 тр' -> '16\\1 тр'
        file_path: TextIO or BinaryIO, optional
            Путь к файлу базы данных

        Returns
        -------
        gunpowder: dict
            Словарь с параметрами пороха
        """
        if isinstance(name, str):
            pass
        else:
            raise ValueError('Название пороха должно быть строкой')
        gunpowders = self.load_database()
        try:
            gunpowder = gunpowders[name]
        except KeyError:
            raise KeyError('Марка пороха не найдена или не существует')
        return self._check_gunpowder(self, gunpowder)
