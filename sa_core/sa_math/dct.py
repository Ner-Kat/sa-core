from enum import Enum

from .dct_versions import *


# DCT variants of realisation
class DctMethod(Enum):
    SCIPY = 0
    MANUAL = 1


# Calculate DCT
def dct(array, method=DctMethod.SCIPY):
    if method == DctMethod.SCIPY:
        return dct_scipy(array)
    elif method == DctMethod.MANUAL:
        return dct_manual(array)


# Calculate Inverse DCT
def idct(array, method=DctMethod.SCIPY):
    if method == DctMethod.SCIPY:
        return idct_scipy(array)
    elif method == DctMethod.MANUAL:
        return idct_manual(array)
