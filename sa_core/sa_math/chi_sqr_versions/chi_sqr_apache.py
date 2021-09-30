# This ChiSquare test created as python port of functions from http://commons.apache.org/proper/commons-math/

import math
import sys
from numpy import isfinite

LANCZOS = [0.99999999999999709182, 57.156235665862923517, -59.597960355475491248, 14.136097974741747174,
           -0.49191381609762019978, 0.33994649984811888699e-4, 0.46523628927048575665e-4, -0.98374475304879564677e-4,
           0.15808870322491248884e-3, -0.021026444172410488319e-3, 0.21743961811521264320e-3,
           -0.16431810653676389022e-3, 0.84418223983852743293e-4, -0.26190838401581408670e-4, 0.36899182659531622704e-5]
HALF_LOG_2_PI = 0.5 * math.log(2.0 * math.pi)
DEFAULT_EPSILON = 10e-15


def logGamma(x):
    if x is None or x <= 0:
        return None

    sum = LANCZOS[0]
    for i in range(1, len(LANCZOS)):
        sum += (LANCZOS[i] / (x + i))

    tmp = x + 0.5 + (607 / 128)
    return ((x + 0.5) * math.log(tmp)) - tmp + HALF_LOG_2_PI + math.log(sum / x)


def regularizedGammaP(a, x):
    return _regularizedGammaP(a, x, DEFAULT_EPSILON, math.pow(2, 32) - 1)


def _regularizedGammaP(a, x, epsilon, maxIterations):
    if a is None or x is None or a <= 0 or x < 0:
        return None

    if x == 0:
        return 0

    if x >= a + 1:
        return 1.0 - _regularizedGammaQ(a, x, epsilon, maxIterations)

    n = 0
    an = 1 / a
    sum = an

    while math.fabs(an / sum) > epsilon and n < maxIterations and sum < math.inf:
        n = n + 1.0
        an = an * (x / (a + n))

        sum = sum + an

    if not isfinite(sum):
        return 1

    return math.exp(-x + (a * math.log(x)) - logGamma(a)) * sum


def _regularizedGammaQ(a, x, epsilon, maxIterations):
    if a is None or x is None or a <= 0 or x < 0:
        return None

    if x == 0:
        return 1

    if x < a + 1:
        return 1 - _regularizedGammaP(a, x, epsilon, maxIterations)

    ret = 1.0 / _continuedFraction(x, epsilon, maxIterations,
                                   lambda n, x: ((2.0 * n) + 1.0) - a + x, lambda n: n * (a - n))

    return math.exp(-x + (a * math.log(x)) - logGamma(a)) * ret


def _continuedFraction(x, epsilon, maxIterations, getA, getB):
    p0 = 1
    p1 = getA(0, x)
    q0 = 0
    q1 = 1
    c = p1 / q1
    n = 0
    relativeError = sys.maxsize

    while n < maxIterations and relativeError > epsilon:
        n += 1
        a = getA(n, x)
        b = getB(n)
        # b = getB(n, x)    # MY CHANGE
        p2 = a * p1 + b * p0
        q2 = a * q1 + b * q0
        infinite = False

        if not isfinite(p2) or not isfinite(q2):
            scaleFactor = 1
            lastScaleFactor = 1
            maxPower = 5
            scale = max(a, b)

            if scale <= 0:
                print("Can't scale")
                sys.exit()

            infinite = True
            for i in range(maxPower):
                lastScaleFactor = scaleFactor
                scaleFactor *= scale
                if a != 0 and a > b:
                    p2 = p1 / lastScaleFactor + (b / scaleFactor * p0)
                    q2 = q1 / lastScaleFactor + (b / scaleFactor * q0)
                elif b != 0:
                    p2 = (a / scaleFactor * p1) + p0 / lastScaleFactor
                    q2 = (a / scaleFactor * q1) + q0 / lastScaleFactor
                infinite = not isfinite(p2) or not isfinite(q2)
                if not infinite:
                    break

        if infinite:
            print("Can't scale")
            sys.exit()

        r = p2 / q2

        if r is None:
            print("NaN divergence")
            sys.exit()

        relativeError = math.fabs(r / c - 1.0)

        c = p2 / q2
        p0 = p1
        p1 = p2
        q0 = q1
        q1 = q2

    if n >= maxIterations:
        print("Non convergent")
        sys.exit()

    return c


def cumulativeProbability(x, degreesOfFreedom):
    if x <= 0:
        return 0

    return regularizedGammaP(degreesOfFreedom / 2, x / 2)


def checkPositive(arr):
    for i in range(len(arr)):
        if arr[i] <= 0:
            print("NOT_POSITIVE_ELEMENT_AT_INDEX " + str(i))
            sys.exit()


def checkNonNegative(arr):
    for i in range(len(arr)):
        if arr[i] < 0:
            print("NEGATIVE_ELEMENT_AT_INDEX " + str(i))
            sys.exit()


def chiSquare(expected, observed):

    if len(expected) < 2:
        print("Dimension mismatch")
        sys.exit()

    if len(expected) != len(observed):
        print("Dimension not equal")
        sys.exit()

    checkPositive(expected)
    checkNonNegative(observed)

    sumExpected = 0
    sumObserved = 0

    for i in range(len(observed)):
        sumExpected += expected[i]
        sumObserved += observed[i]

    ratio = 1
    rescale = False

    if math.fabs(sumExpected - sumObserved) > 10E-6:
        ratio = sumObserved / sumExpected
        rescale = True

    sumSq = 0
    for i in range(len(observed)):
        if rescale:
            dev = observed[i] - ratio * expected[i]
            sumSq += dev * dev / (ratio * expected[i])
        else:
            dev = observed[i] - expected[i]
            sumSq += dev * dev / expected[i]

    return sumSq


def chi_sqr(observed, expected):
    chi2 = chiSquare(expected, observed)
    p = 1 - cumulativeProbability(chi2, len(expected) - 1)
    return chi2, p
