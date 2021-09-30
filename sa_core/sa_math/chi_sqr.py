from enum import Enum

from .chi_sqr_versions import *


# ChiSquare variants of realisation
class ChiSqrMethod(Enum):
    SCIPY = 0
    MANUAL = 1
    APACHE = 2


methods = [chi_sqr_scipy, chi_sqr_manual, chi_sqr_apache]


# Calculate ChiSquare test
def chi_sqr(observed, expected, method=ChiSqrMethod.APACHE):
    if len(observed) != len(expected):
        raise ValueError("Observed and expected values arrays must be the same length")

    return methods[method.value](observed, expected)
