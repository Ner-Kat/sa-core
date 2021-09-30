from scipy.fftpack import dct as pydct, idct as pyidct


def dct(array):
    return pydct(array, norm='ortho')


def idct(array):
    return pyidct(array, norm='ortho')
