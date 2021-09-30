import numpy as np
import random
from math import fabs

from .kz_config import *
from sa_core.sa_math import dct, idct


# Gathers blocks to image array
def blocks_to_imar(img_array, blocks, block_size=BLOCK_SIZE):
    height, width, deep = img_array.shape

    block_ind = 0
    for i in range(height // block_size):
        for j in range(width // block_size):
            for bi in range(block_size):
                for bj in range(block_size):
                    img_array[i * block_size + bi][j * block_size + bj][2] = blocks[block_ind][bi][bj]
            block_ind += 1

    return img_array


# Splits image array to blocks
def get_blocks(img_array, block_size=BLOCK_SIZE):
    height, width = img_array.shape
    blocks = []

    for i in range(height // block_size):
        for j in range(width // block_size):
            block = np.zeros((block_size, block_size))
            for bi in range(block_size):
                for bj in range(block_size):
                    block[bi][bj] = img_array[i * block_size + bi][j * block_size + bj]
            blocks.append(block)

    return blocks


# Truncates values out of color range and round pixel values for all blocks
def normalize_all_blocks(blocks, block_size=BLOCK_SIZE):
    for block_ind in range(len(blocks)):
        blocks[block_ind] = normalize_block(blocks[block_ind], block_size)
    return blocks


# Truncates values out of color range into one block and round pixel values
def normalize_block(block, block_size=BLOCK_SIZE):
    for i in range(block_size):
        for j in range(block_size):
            if block[i][j] > 255:
                block[i][j] = int(255)
            elif block[i][j] < 0:
                block[i][j] = int(0)
            else:
                block[i][j] = int(round(block[i][j]))
    return block


# Generates random indexes
def get_random_indexes(blocks_num, seed, indexes_num):
    random.seed(seed)

    linear_inds = [i for i in range(blocks_num)]
    inds = random.sample(linear_inds, k=blocks_num)

    return inds[:indexes_num]


# Calculates DCT coefficients matrix for each block
def get_dct_blocks(blocks):
    dct_blocks = []
    for block in blocks:
        dct_blocks.append(dct(block, DCT_METHOD))
    return dct_blocks


# Calculates IDCT values matrix (pixels block) for each DCT matrix
def get_idct_blocks(blocks):
    idct_blocks = []
    for block in blocks:
        idct_blocks.append(idct(block, DCT_METHOD))
    return idct_blocks


# Returns coefficients at these indexes
def get_block_coeffs(block, indexes=DCT_COEFFICIENTS):
    return block[indexes[0][0]][indexes[0][1]], block[indexes[1][0]][indexes[1][1]]


# Returns difference between absolute values of two arguments
def get_moduluses_difference(n1, n2):
    return fabs(n1) - fabs(n2)


# Returns modified dct coefficients that encode a bit
def get_modified_coeffs(inc_first, bc, threshold):
    n1 = fabs(bc[0])
    n2 = fabs(bc[1])
    dif = get_moduluses_difference(n1, n2)

    if inc_first:
        while dif <= threshold:
            n1 += 1
            if n2 > 0:
                n2 -= 1
            dif = get_moduluses_difference(n1, n2)
    else:
        while dif >= threshold:
            n2 += 1
            if n1 > 0:
                n1 -= 1
            dif = get_moduluses_difference(n1, n2)

    if bc[0] < 0:
        n1 = -n1
    if bc[1] < 0:
        n2 = -n2

    return n1, n2
