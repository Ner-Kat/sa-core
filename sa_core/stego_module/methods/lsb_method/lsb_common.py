import random
import numpy as np

from .lsb_config import *


# Returns pseudo-random generated indexes for 3-dimensional pixels array
def generate_indexes(width, height, deep, seed, count):
    random.seed(seed)

    whole_size = height * width * deep
    linear_indexes = [i for i in range(whole_size)]
    linear_indexes = random.sample(linear_indexes, k=count)

    indexes = []
    for ind in linear_indexes:
        pixel_ind = ind // deep  # Getting index in width x height matrix
        real_ind = pixel_ind // width, pixel_ind % width, ind % deep  # Getting three pixel indexes

        indexes.append(real_ind)

    return indexes


# Returns pseudo-random generated indexes for linear array
def generate_indexes_for_linear_array(length, seed, count):
    random.seed(seed)

    indexes = [i for i in range(length)]
    indexes = random.sample(indexes, k=length)

    return indexes[:count]


# Converts 3-dimensional image array to linear array
def imar_to_linear(imar):
    height, width, deep = imar.shape
    linear_imar = [imar[i][j][ch] for i in range(height) for j in range(width) for ch in range(3)]
    return linear_imar


# Converts linear array to 3-dimensional image array
def linear_imar_to_imar(linear_imar, sizes, dtype=np.int32):
    height, width, deep = sizes
    imar = np.zeros(sizes, dtype)

    k = 0
    for i in range(height):
        for j in range(width):
            for ch in range(3):
                if k >= len(linear_imar):
                    return None

                imar[i][j][ch] = linear_imar[k]
                k += 1

    return imar
