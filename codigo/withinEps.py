import numpy as np


def within_eps(a, b, epsilon):
    if np.fabs(a - b) < epsilon:
        return True
    return False
