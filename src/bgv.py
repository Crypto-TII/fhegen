from sage.all import var
import config
import math
import util


def _Bclean(m, t, D, Vs, Ve):
    d = util.phi(m)
    return D * t * math.sqrt(d * (1 / 12 + 2 * d * Vs * Ve + Ve))


def _Bconst(const, m, t, D, Vs, Ve):
    if not const:
        return 1

    d = util.phi(m)
    return D * t * math.sqrt(d / 12)


def _Bscale(m, t, D, Vs, Ve):
    d = util.phi(m)
    return D * t * math.sqrt(d / 12 * (1 + d * Vs))


def _Bswitch(m, t, D, Vs, Ve, method, L, beta, omega):
    d = util.phi(m)
    B = D * t * d * math.sqrt(Ve / 12)

    f0 = {
        'BV': beta * math.sqrt(math.log(1 << (L * config.BITS), beta)),
        'BV-RNS': beta * math.sqrt(L * math.log(1 << config.BITS, beta)),
        'GHS': 1 / config.K,
        'GHS-RNS': math.sqrt(L) / pow(config.K, L),
        'Hybrid': math.sqrt(math.log(1 << (L * config.BITS), beta)) / config.K,
        'Hybrid-RNS': math.sqrt(omega * L) / pow(config.K, L)
    }[method]
    f1 = {
        'BV': 0,
        'BV-RNS': 0,
        'GHS': 1,
        'GHS-RNS': L,
        'Hybrid': 1,
        'Hybrid-RNS': math.ceil(L / omega)
    }[method]

    return f0 * B + f1 * _Bscale(m, t, D, Vs, Ve)


def _fscale(method, L, beta, omega):
    return math.sqrt({
        'BV': 1,
        'BV-RNS': 1,
        'GHS': 1,
        'GHS-RNS': L,
        'Hybrid': 1,
        'Hybrid-RNS': math.ceil(L / omega)
    }[method])


def _B(ops, Bargs, kswargs):
    model = ops['model']
    sums = ops['sums']
    rots = ops['rots']
    const = ops['const']

    Bconst = _Bconst(const, **Bargs)
    Bscale = _Bscale(**Bargs)
    Bswitch = _Bswitch(**Bargs, **kswargs)
    fscale = _fscale(**kswargs)

    B = var('B')
    f = {
        'Base': ((sums * Bconst * B)**2 + Bswitch) / (B - fscale * Bscale),
        'Model1': (sums**2 * (Bconst * B + rots * Bswitch)**2 + Bswitch) / (B - fscale * Bscale),
        'Model2': (sums**2 * Bconst**2 * (B + rots * Bswitch)**2 + Bswitch) / (B - fscale * Bscale),
        'OpenFHE': (sums * B**2 + (rots + 1) * Bswitch) / (B - fscale * Bscale)
    }[model]
    return f.find_local_minimum(fscale * Bscale, 1 << config.BITS)[1]


def _B0(ops, B, Bargs, kswargs, c=1):
    model = ops['model']
    sums = ops['sums']
    rots = ops['rots']
    const = ops['const']

    Bconst = _Bconst(const, **Bargs)
    Bswitch = _Bswitch(**Bargs, **kswargs)

    return {
        'Base': 2 * c * (sums * Bconst * B)**2,
        'Model1': 2 * c * sums**2 * (Bconst * B + rots * Bswitch)**2,
        'Model2': 2 * c * sums**2 * Bconst**2 * (B + rots * Bswitch)**2,
        'OpenFHE': 2 * c * sums * B**2 + rots * Bswitch
    }[model]


def _logp0(B0):
    return util.clog2(B0)


def _logpi(B):
    return util.clog2(B)


def _logpM(B, Bargs):
    Bclean = _Bclean(**Bargs)
    Bscale = _Bscale(**Bargs)

    return util.clog2(Bclean / (B - Bscale))


def _logP(logq, kswargs, K=config.K):
    method = kswargs['method']
    beta = kswargs['beta']
    omega = kswargs['omega']

    L = len(logq)
    logp = logq[1]
    logK = int(math.log2(K))
    logb = int(math.log2(beta))

    if method.startswith('BV'):
        return None
    elif method.startswith('GHS'):
        return logK + L * logp
    elif method == 'Hybrid':
        return logK + logb + int(math.log2(math.sqrt(L * logp / logb)))
    else:  # method == 'Hybrid-RNS'
        return logK + int(math.log2(math.sqrt(omega * L))) + int(math.ceil(L * logp / omega))


def logqP(ops, Bargs, kswargs, sdist):
    B = _B(ops, Bargs, kswargs)
    B0 = _B0(ops, B, Bargs, kswargs)

    logq = [_logp0(B0)]
    for _ in range(ops['muls'] - 1):
        logq.append(_logpi(B))
    logq.append(_logpM(B, Bargs))
    logP = _logP(logq, kswargs)

    return logq, logP
