# Encapsulates different realisations of Discrete cosine transform (DCT)

from .dct_scipy import dct as dct_scipy, idct as idct_scipy
from .dct_manual import dct as dct_manual, idct as idct_manual

__all__ = ['dct_scipy', 'idct_scipy', 'dct_manual', 'idct_manual']
