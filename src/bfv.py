import config
import math
import util


def _f(x, sdist):
    if sdist == 'Ternary':
        alpha = 0.22
        beta = 2.43
        gamma = 8.95
    else:
        # TODO: sdist == 'Error'
        raise NotImplementedError("sdist == 'Error'")

    return -(1 / math.exp(alpha * x - beta)) + gamma


def _Vclean(m, t, D, Vs, Ve):
    d = util.phi(m)
    return t**2 * d * Ve * (Vs + Ve)


def _Vconst(const, m, t, D, Vs, Ve):
    if not const:
        return 1

    d = util.phi(m)
    return t**2 * d / 12


def _Vmul(V, sdist, m, t, D, Vs, Ve):
    d = util.phi(m)
    return t**2 * d**2 * Vs / 6 * V * _f(2, sdist)


def _Vscale(m, t, D, Vs, Ve):
    d = util.phi(m)
    return t**2 / 12 * (1 + d * Vs)


def _Vswitch(m, t, D, Vs, Ve, method, L, beta, omega):
    d = util.phi(m)
    V = t**2 * d * Ve / 12

    f0 = {
        'BV': beta**2 * math.log(1 << (L * config.BITS), beta),
        'BV-RNS': beta**2 * L * math.log(1 << config.BITS, beta),
        'GHS': 1 / config.K**2,
        'GHS-RNS': L / pow(config.K, L**2),
        'Hybrid': math.log(1 << (L * config.BITS), beta) / config.K**2,
        'Hybrid-RNS': omega * L / pow(config.K, L**2)
    }[method]
    f1 = {
        'BV': 0,
        'BV-RNS': 0,
        'GHS': 1,
        'GHS-RNS': L**2,
        'Hybrid': 1,
        'Hybrid-RNS': math.ceil(L / omega)**2
    }[method]

    return f0 * V + f1 * _Vscale(m, t, D, Vs, Ve)


def _Vlevel(V, ops, Bargs, kswargs, sdist):
    model = ops['model']
    sums = ops['sums']
    rots = ops['rots']
    const = ops['const']

    Vconst = _Vconst(const, **Bargs)
    Vswitch = _Vswitch(**Bargs, **kswargs)

    return {
        'Base': sums * Vconst * V,
        'Model1': sums * (Vconst * V + rots * Vswitch),
        'Model2': sums * Vconst * (V + rots * Vswitch),
        'OpenFHE': sums * V + rots * Vswitch
    }[model]


def _logq(ops, Bargs, kswargs, sdist):
    muls = ops['muls']
    D = Bargs['D']

    V = _Vclean(**Bargs)
    for _ in range(muls):
        V = _Vlevel(V, ops, Bargs, kswargs, sdist)
        V = _Vmul(V, sdist, **Bargs) + _Vswitch(**Bargs, **kswargs)

    return util.clog2(D * math.sqrt(8 * V))


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
    logq = _logq(ops, Bargs, kswargs, sdist)
    logP = _logP(logq, kswargs)

    return [logq], logP
