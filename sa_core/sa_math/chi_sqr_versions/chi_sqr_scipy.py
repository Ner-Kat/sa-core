from scipy.stats import chisquare


def chi_sqr(observed, expected):
    chi2, p = chisquare(observed, expected)
    return chi2, 1 - p
