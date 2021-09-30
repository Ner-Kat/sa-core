# Encapsulates different variants of ChiSquare test realisation

from .chi_sqr_scipy import chi_sqr as chi_sqr_scipy
from .chi_sqr_manual import chi_sqr as chi_sqr_manual
from .chi_sqr_apache import chi_sqr as chi_sqr_apache

__all__ = ['chi_sqr_scipy', 'chi_sqr_manual', 'chi_sqr_apache']
