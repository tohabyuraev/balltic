import os
import json


PATH = os.getcwd()


def _load_gpowders() -> dict:
    try:
        with open(PATH + r'\powders\gpowders.json') as f:
            gpowders = json.load(f)
    except Exception:
        raise Exception
    return gpowders


def _save_gpowders(gpowders: dict) -> json:
    try:
        with open(PATH + r'\powders\gpowder.json', 'w') as f:
            json.dump(gpowders, f)
    except Exception:
        raise Exception


def show_all():
    """
    Show all gunpowders names from gpowders.json

    Parameters
    ----------
    No parameters

    Returns
    -------
    names: list
        List with gunpowders names
    """

    gpowders = _load_gpowders()
    print(gpowders.keys())


def show_one(gpname: str):
    """
    Show gunpowder characteristics

    Parameters
    ----------
    gpname: str
        Gunpowder name

    Returns
    -------
    char: str
        Gunpowder characteristics
    """

    gpowders = _load_gpowders()
    print(gpowders[gpname])


def check(gpname: str):
    """
    Checks for gunpowder in gpowders.json

    Parameters
    ----------
    gpname: str
        Gunpowder name

    Returns
    -------
    : bool
        `True` if gunpowder in gpowders.json, `False` otherwise
    """

    gpowders = _load_gpowders()
    return True if gpname in gpowders else False


def fetch(gpname: str):
    """"
    Gives gunpowder

    Parameters
    ----------
    gpname: str
        Gunpowder name

    Returns
    -------
    gpowder: dict
        Gunpowder in dictionary form
    """

    gpowders = _load_gpowders()
    return gpowders[gpname]


def add(gpname: str, gpowder: dict):
    """
    Add new gunpowder in gpowders.json

    Parameters
    ----------
    gpname: str
        Gunpowder name
    gpowder: dict
        Gunpowder characteristics. See Notes

    Returns
    -------
    : bool
        `True` if all positive, `False` otherwise

    Notes
    -----
    Gunpowder has several characteristics (in dictionary form):
        name, f, etta, alpha_k, T_1, ro, I_k, Z_k, k_1, lambda_1,
        k_2, lambda_2, k_f, k_l
    """

    gpowders = _load_gpowders()
    gpowders[gpname] = gpowder
    try:
        _save_gpowders(gpowders)
    except Exception:
        return False
    else:
        return True


def delete(gpname: str):
    """
    Delete gunpowder from gpowders.json

    Parameters
    ----------
    gpname: str
        Gunpowder name

    Returns
    -------
    : bool
        `True` if all positive, `False` otherwise
    """

    gpowders = _load_gpowders()
    try:
        del gpowders[gpname]
    except Exception:
        return True
    else:
        return False
