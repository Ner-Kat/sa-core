from decimal import Decimal, getcontext
import math
import scipy.integrate
import scipy.special


def chi_sqr(observed, expected):
    getcontext().prec = 100

    k = len(expected)
    chi2 = 0

    for i in range(k):
        chi2 += math.pow(observed[i] - expected[i], 2) / expected[i]

    ex = (k - 1) / 2
    a = Decimal(1 / (pow(2, ex) * scipy.special.gamma(ex)))
    integral = Decimal(scipy.integrate.quad(under_integral, 0, chi2, args=(k,))[0])
    p = Decimal(1 - Decimal(a * integral))

    return chi2, p


def under_integral(x, k):
    d_x = Decimal(x)

    d_first = Decimal(math.exp(- x / 2))
    to_pow = Decimal((k - 1) / 2 - 1)
    d_sec = Decimal(d_x ** to_pow)

    d_res = Decimal(d_first * d_sec)

    return Decimal(d_res)
