import config
import util


def gent(m, logt, batch):
    return util.genprime(2**(logt - 1), m, batch)


def genq(mods, P):
    logq = [mods.first(P)]
    for _ in range(mods.depth - 2):
        logq.append(mods.middle(P))
    logq.append(mods.last(P))

    return logq


def genqP(mods):
    logq = genq(mods, None)
    for i in range(config.PARAMS_QPREPS):
        logP = mods.switch(logq)
        logq = genq(mods, 2**logP)

    return logq, logP


def genm(sec, t, logt, batch, mods, secret, pow2):
    newt = True if not t else False

    m = 4
    while True:
        if newt:
            t = gent(m, logt, batch)
        mods.update(m, t)
        logq, logP = genqP(mods)

        if util.estsecurity(m, sum(logq) + logP, secret) > sec:
            break
        m <<= 1

    if pow2:
        return m, t, logq, logP

    raise NotImplementedError("pow2 == False")
