__author__ = 'Anthony Byuraev'

__all__ = ['GunPowder']

import os
import json
import typing
from abc import ABCMeta, abstractclassmethod, abstractmethod


BASE_PATH = os.getcwd()
GPOWDER_KEYS = (
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

    @abstractclassmethod
    def load_db(self, fp: typing.IO[str] = None) -> typing.Dict[str, dict]:
        pass

    @abstractclassmethod
    def load_gpowder(self, name: str) -> dict:
        pass

    @abstractmethod
    def _check_gpowder(self, gpowder: dict) -> dict:
        pass


class GunPowder(BasePowder):
    """
    Реализация артиллерийского пороха
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self._gpowder = self.load_gpowder(self.name)

        self.k = self._gpowder['etta'] + 1
        self.f = self._gpowder['f'] * 1e6
        self.ro = self._gpowder['ro'] * 1e3
        self.k_1 = self._gpowder['k_1']
        self.k_2 = self._gpowder['k_2']
        self.I_k = self._gpowder['I_k'] * 1e6
        self.z_k = self._gpowder['Z_k']
        # self.T_1 = self._gpowder['T_1']
        self.alpha_k = self._gpowder['alpha_k'] * 1e-3
        self.lambda_1 = self._gpowder['lambda_1']
        self.lambda_2 = self._gpowder['lambda_2']

    def __str__(self):
        return str(self._gpowder)

    def __repr__(self):
        return 'GunPowder("gunpowder_name")'

    @classmethod
    def load_db(self, fp: typing.IO[str] = None) -> typing.Dict[str, dict]:
        """
        Загружает все пороха из базы данных, расположенной в
            balltic\\powders\\gpowders.json

        Parameters
        ----------
        fp: TextIO or BinaryIO, optional
            Путь к файлу базы данных
        """
        if fp is not None:
            file_path = fp
        else:
            file_path = '\\balltic\\powders\\gpowders.json'
        try:
            with open(BASE_PATH + file_path) as file_:
                return json.load(file_)
        except FileNotFoundError:
            raise FileNotFoundError('Файл не найден или не существует')

    @classmethod
    def load_gpowder(self, name: str) -> dict:
        """
        Загружает по названию порох из базы данных, расположенной в
            "balltic\\powders\\gpowders.json"

        Parameters
        ----------
        name: str
            Название пороха. Следует писать дробь через двойной обратный слэш
            Пример:
                '16/1 тр' -> '16\\1 тр'
        fp: TextIO or BinaryIO, optional
            Путь к файлу базы данных

        Returns
        -------
        gpowder: dict
            Словарь с параметрами пороха
        """
        if isinstance(name, str):
            pass
        else:
            raise ValueError('Название пороха должно быть строкой')
        gpowders = self.load_db()
        try:
            gpowder = gpowders[name]
        except KeyError:
            raise KeyError('Марка пороха не найдена или не существует')
        return self._check_gpowder(self, gpowder)

    def _check_gpowder(self, gpowder: dict) -> dict:
        for key in GPOWDER_KEYS:
            try:
                gpowder[key]
            except KeyError:
                raise KeyError('Параметр пороха не существует')
        return gpowder
