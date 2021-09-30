import numpy as np
from math import sqrt, cos, pi


def dct(array):
    N = array.shape[0]
    dct = np.zeros((N, N))

    for u in range(N):
        for v in range(N):
            dct_elem = (su(u) * su(v)) / sqrt(2 * N)
            sum = 0
            for x in range(N):
                for y in range(N):
                    cos1 = cos((pi * u * (2 * x + 1)) / (2 * N))
                    cos2 = cos((pi * v * (2 * y + 1)) / (2 * N))
                    sum += array[x][y] * cos1 * cos2
            dct_elem *= sum
            dct[u, v] = dct_elem

    return dct


def idct(array):
    N = array.shape[0]
    arr = np.zeros((N, N))

    for x in range(N):
        for y in range(N):
            arr_elem = 1 / sqrt(2 * N)
            sum = 0
            for u in range(N):
                for v in range(N):
                    cos1 = cos((pi * u * (2 * x + 1)) / (2 * N))
                    cos2 = cos((pi * v * (2 * y + 1)) / (2 * N))
                    sum += su(u) * su(v) * array[u][v] * cos1 * cos2
            arr_elem *= sum
            arr[x, y] = arr_elem

    return arr


def su(u):
    if u == 0:
        return 1 / sqrt(2)
    elif u > 0:
        return 1

    return None
