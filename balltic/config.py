P_CANNON = {
    'nodes': 100,
    'initialp': 5e6,
    'ro': 141.471,
    'chamber': 0.5,
    'barrel': 2,
    'caliber': 0.03,
    'shell': 0.1,
    'k': 1.4,
    'Ku': 0.5,
    'R': 287,
}

G_CANNON = {
    'nodes': 100,
    'boostp': 30 * 1e6,
    'press_vsp': 5 * 1e6,
    'denload': 775,
    'K': 1.03,
    'fi_1': 1.02,
    'caliber': 0.057,
    'shell': 3.75,
    'barrel': 3.027,
    'kurant': 0.4,
    'omega_q': 0.257,
}

DEFAULT_GP = None

AVERAGE_GP = {
    'f': 1e6,
    'k': 1.25,
    'ro': 1.6e3,
    'alpha_k': 1e-3,
    'kappa_1': 1,
    'lambda_1': 0,
}
