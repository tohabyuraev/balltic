P_CANNON = {
    'k': 1.4,
    'R': 287,
    'ro': 141.471,
    'nodes': 100,
    'shell': 0.1,
    'kurant': 0.5,
    'barrel': 2,
    'chamber': 0.5,
    'caliber': 0.03,
    'initialp': 5e6,
}

G_CANNON = {
    'K': 1.03,
    'fi_1': 1.02,
    'nodes': 100,
    'shell': 3.75,
    'boostp': 30 * 1e6,
    'barrel': 3.027,
    'kurant': 0.4,
    'denload': 775,
    'caliber': 0.057,
    'omega_q': 0.257,
    'press_vsp': 5 * 1e6,
}

DEFAULT_GP = {
    'name': '16\\1 тр',
    'f': 1.004,
    'ro': 1.6,
    'k_1': 0.0016,
    'k_2': 0.0,
    'I_k': 1.13,
    'Z_k': 1.0, 
    'T_1': 2895.0,
    'etta': 1.225,
    'alpha_k': 1.012,
    'lambda_1': 0.0,
    'lambda_2': 0.0,
}

AVERAGE_GUNPOWDER = {
    'f': 1e6,
    'k': 1.25,
    'ro': 1.6e3,
    'alpha_k': 1e-3,
    'kappa_1': 1,
    'lambda_1': 0,
}
