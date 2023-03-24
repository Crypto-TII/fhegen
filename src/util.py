import math

from sage.all import euler_phi
from sage.all import Integer, Mod, Primes


def clog2(x):
    return int(math.ceil(math.log2(x)))


def phi(x):
    return euler_phi(x)


def estsecurity(m, logq, sdist):
    d = phi(m)

    if sdist == 'Ternary':
        alpha = 0.05
        beta = 0.33
        gamma = 17.88
        delta = 0.65
    elif sdist == 'Error':
        alpha = 8.82
        beta = 0.89
        gamma = 10.40
        delta = -0.02

    est = -math.log2(alpha * logq / d) * beta * d / logq + gamma * pow(logq / d, delta) * math.log2(d / logq)
    return max(int(math.floor(est)), 0)


def genprime(start, m=0, batch=False):
    P = Primes()

    p = P.next(Integer(start))
    if batch:
        while p % m != 1:
            p = P.next(p)

    return p


def gent(m, gen, t, logt, batch):
    if gent:
        return genprime(2**(logt - 1), m, batch)
    else:
        return t


def slots(m, t):
    return euler_phi(m) / Mod(t, m).multiplicative_order()
