import codegen
import config
import interactive
import math
import util


def bounds(d, t, Vs, Ve=3.2**2, D=6):
    Bclean = D * t * math.sqrt(d * (1/12 + 2 * d * Vs * Ve + Ve))
    Bks    = D * t * d * math.sqrt(Ve / 12)
    Bscale = D * t * math.sqrt(d / 12 * (1 + d * Vs))
    Bconst = D * t * math.sqrt(d / 12)

    return Bclean, Bks, Bscale, Bconst


def genq(m, t, logt, batch, ops, keyswitch, omega, bargs):
    muls, const, rots, sums = ops

    if not t:
        t = util.genprime(2**(logt - 1), m, batch)

    d = util.phi(m)
    Bclean, Bks, Bscale, Bconst = bounds(d, t, *bargs)
    q = [util.genprime(math.ceil(4 * Bscale), m, True)]

    xi = sums
    if const:
        xi *= Bconst**2

    if rots == 0:
        q.append(util.genprime(math.ceil(4 * xi * Bscale), m, True))
    else: # rots > 0
        if keyswitch == 'BV':
            parens = rots * omega * math.sqrt(muls + 1) * math.log(Bks, omega) * Bks + Bconst
        else:
            parens = rots + Bconst
        q.append(util.genprime(math.ceil(4 * sums**2 * Bconst * Bscale * parens), m, True))
    for _ in range(muls):
        q.append(util.genprime(q[-1], m, True))

    if rots == 0:
        q.append(util.genprime(math.ceil(Bclean / Bscale), m, True))
    else: # rots > 0
        if keyswitch == 'BV':
            parens = 2 * rots * omega * math.sqrt(muls + 1) * math.log(Bks, omega) * Bks / Bconst + 1
        else:
            parens = rots / Bconst + 1
        q.append(util.genprime(math.ceil(Bclean / (parens * Bscale)), m, True))

    return q, util.flog2(int(math.prod(q)))


def genm(sec, qargs, secret, pow2=True):
    m = 4

    while True:
        _, logq = genq(m, *qargs)
        est     = util.estsecurity(m, logq, secret)

        if est > sec:
            break

        m <<= 1

    if pow2:
        return m

    raise NotImplementedError("pow2 == False")


def genP(m, t, q, ops, keyswitch, omega, bargs, k=10):
    _, const, rots, sums = ops

    if keyswitch not in ['GHS', 'Hybrid']:
        raise ValueError("keyswitch not in ['GHS', 'Hybrid']")

    d = util.phi(m)
    qneg2 = int(math.prod(q[:-1]))
    Bclean, Bks, Bscale, Bconst = bounds(d, t, *bargs)

    if keyswitch == 'GHS':
        Pbound = k * qneg2 * Bks / Bscale
        if rots == 0:
            Pbound /= q[-2]
        logP = util.clog2(Pbound)
    else: # keyswitch == 'Hybrid'
        logP = util.clog2(k * omega * math.sqrt(math.log(qneg2, omega)) * Bks / Bscale)

    return None, logP


if __name__ == "__main__":
    interactive.welcome()
    t, logt = interactive.gett()
    if t:
        secdef = 'Order/security'
    else:
        secdef = 'Security/order'

    if interactive.setsecurity(secdef, t):
        m, sec = None, interactive.getsecurity()
        pow2   = interactive.usepow2()
    else:
        m, sec = interactive.getm(), None
    print()

    muls  = interactive.getmuls()
    const = interactive.doconst()
    rots  = interactive.getrots()
    sums  = interactive.getsums()
    lib   = interactive.getlib()

    batch     = False
    keyswitch = 'Hybrid'
    omega     = 4
    secret    = 'Ternary'
    sigma     = 3.2
    D         = 6

    if lib == 'PALISADE':
        batch = True

    if interactive.setadvanced():
        print()
        batch     = interactive.fullbatch(lib)
        secret    = interactive.getsecret(lib)
        keyswitch = interactive.getkeyswitch(lib)

        if keyswitch in ['BV', 'Hybrid']:
            omega = interactive.getomega(keyswitch)
        else:
            omega = 1

    Ve = sigma * sigma
    Vs = { 'Ternary': 2/3, 'Error': Ve }[secret]
    if secret == 'Error':
        raise NotImplementedError("secret == 'Error'")

    ops  = muls, const, rots, sums
    args = t, logt, batch, ops, keyswitch, omega, (Vs, Ve, D)
    if not m:
        m = genm(sec, args, secret, pow2)
    if not t:
        t = util.genprime(2**(logt - 1), m, batch)

    q, logq = genq(m, *args)
    sec     = max(util.estsecurity(m, logq, secret), 0)

    args = m, t, q, ops, keyswitch, omega, (Vs, Ve, D)
    if keyswitch in ['GHS', 'Hybrid']:
        _, logP = genP(*args)
    else:
        logP = None

    if lib == 'HElib' and util.gcd(m, t) != 1:
        raise ValueError("HElib requires gcd(m, t) == 1")
    if lib == 'PALISADE' and t % m != 1:
        raise ValueError("PALISADE requires t % m == 1")
    if lib == 'PALISADE' and const:
        raise ValueError("PALISADE does not support scalar multiplication")
    interactive.config(sec, m, t, q, logP, lib)

    if lib == 'HElib':
        interactive.writelib(lib)
        codegen.writehelib(m, t, logq, logP, ops, keyswitch, omega, D)
    elif lib == 'PALISADE':
        interactive.writelib(lib)
        if logP > 60:
            interactive.warnlogP()

        logq0 = util.flog2(q[0])
        logql = util.flog2(max(q[1], q[-1]))
        codegen.writepalisade(m, t, logq0, logql, ops, keyswitch, omega, secret)
