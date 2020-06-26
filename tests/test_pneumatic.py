import math

import pytest

from balltic import Pneumatic
from balltic.config import PNEUMATIC_CANNON
from .dataset import PNEUMATIC_CANNON as cannon

def test_init():
    sol = Pneumatic(cannon, nodes=350, barrel=5.098)

    assert sol.default == PNEUMATIC_CANNON

    assert sol.nodes == 350
    assert sol.press == cannon['initialp']
    assert sol.ro == cannon['ro']
    assert sol.chamber == cannon['chamber']
    assert sol.barrel == 5.098
    assert sol.square == math.pi * cannon['caliber'] ** 2 / 4
    assert sol.shell == sol.default['shell']
    assert sol.k == cannon['k']
    assert sol.kurant == cannon['Ku']
    assert sol.R == cannon['R']
