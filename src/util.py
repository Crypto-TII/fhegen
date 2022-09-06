import math

from sage.all import euler_phi, gcd
from sage.all import Integer, Mod, Primes


def clog2(x):
    return math.ceil(math.log2(x))


def flog2(x):
    return math.floor(math.log2(x))


def phi(x):
    return euler_phi(x)


def estsecurity(m, logq, secret):
    d = phi(m)
    if secret == 'Ternary':
        alpha = 0.07
        beta  = 0.34
        gamma = 18.53
    elif secret == 'Error':
        alpha = 0.65
        beta  = 0.53
        gamma = 22.88

    return -math.log2(alpha * logq / d) * beta * d / (logq) + gamma * math.sqrt(logq / d) * math.log2(d / logq)


def genprime(start, m=0, batch=False):
    P = Primes()

    p = P.next(Integer(start))
    if batch:
        while p % m != 1:
            p = P.next(p)

    return p


def slots(m, t):
    return euler_phi(m) / Mod(t, m).multiplicative_order()
