import codegen
import config
import interactive
import util


class Bounds:
    def __init__(self, m, t, Vs, Ve=3.2**2, D=6):
        d = util.phi(m)

        self.m      = m
        self.clean  = util.ceil(D * t * util.csqrt(d * (1/12 + 2 * d * Vs * Ve + Ve)))
        self.switch = util.ceil(D * t * d * util.csqrt(Ve / 12))
        self.scale  = util.ceil(D * t * util.csqrt(d / 12 * (1 + d * Vs)))
        self.const  = util.ceil(D * t * util.csqrt(d / 12))


class Mods:
    def __init__(self, B, mul, const, rot, sum, bits=64):
        self.B = B
        self.mul = mul
        self.const = const
        self.rot = rot
        self.sum = sum
        self.bits = bits

    def first(self, keyswitch, omega, P=1):
        if self.const == 0:
            Bconst = 1
        else:
            Bconst = self.B.const

        logw = lambda x: util.clog(x, omega)
        xi = (self.sum * Bconst)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(util.clog(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return 8 * xi * self.B.scale**2
            elif keyswitch == 'BV-RNS':
                return 8 * xi * (self.B.scale + util.csqrt(self.mul) * self.B.switch)**2
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return 8 * lenP * xi * self.B.scale**2
        else:
            if keyswitch == 'BV':
                return 8 * self.sum**2 * (2 * self.rot * omega * util.csqrt(self.mul) * logw(self.B.switch) * self.B.switch + Bconst * self.B.scale)**2
            elif keyswitch == 'BV-RNS':
                return 32 * self.sum**2 * self.rot**2 * (2 * self.mul + 1) * self.B.switch**2
            elif keyswitch in ['GHS', 'Hybrid']:
                return 8 * self.sum**2 * (self.rot + Bconst)**2 * self.B.scale**2
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                return 8 * lenP * self.sum**2 * (self.rot + Bconst)**2 * self.B.scale**2

    def middle(self, keyswitch, omega, P=1):
        if self.const == 0:
            Bconst = 1
        else:
            Bconst = self.B.const

        logw = lambda x: util.clog(x, omega)
        xi = (self.sum * Bconst)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(util.clog(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return 4 * xi * self.B.scale
            elif keyswitch == 'BV-RNS':
                return 4 * xi * (self.B.scale + util.csqrt(self.mul) * self.B.switch)
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return 4 * xi * util.csqrt(lenP) * self.B.scale
        else:
            if keyswitch == 'BV':
                return self.sum**2 * Bconst * (4 * self.rot * omega * util.csqrt(self.mul) * logw(self.B.switch) * self.B.switch + Bconst * self.B.scale)
            elif keyswitch == 'BV-RNS':
                return 4 * self.sum**2 * self.rot * util.csqrt(self.mul) * Bconst * self.B.switch
            elif keyswitch in ['GHS', 'Hybrid']:
                return 4 * self.sum**2 * (self.rot + Bconst) * Bconst * self.B.scale
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                return 4 * self.sum**2 * util.csqrt(lenP) * (self.rot + Bconst) * Bconst * self.B.scale

    def last(self, keyswitch, omega, P=1):
        if self.const == 0:
            Bconst = 1
        else:
            Bconst = self.B.const

        logw = lambda x: util.clog(x, omega)
        xi = (self.sum * Bconst)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(util.clog(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return util.ceil(self.B.clean / self.B.scale)
            elif keyswitch == 'BV-RNS':
                return util.ceil(self.B.clean / (self.B.scale + 2 * util.csqrt(self.mul) * self.B.switch))
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return util.ceil(self.B.clean / ((2 * util.csqrt(lenP) - 1) * self.B.scale))
        else:
            if keyswitch == 'BV':
                return util.ceil(self.B.clean * Bconst / (2 * self.rot * omega * util.csqrt(self.mul) * logw(self.B.switch) * self.B.switch))
            elif keyswitch == 'BV-RNS':
                return util.ceil(self.B.clean / (16 * self.sum**2 * self.rot**2 * self.mul * self.B.switch**2 - self.B.scale))
            elif keyswitch in ['GHS', 'Hybrid']:
                return util.ceil(self.B.clean / ((self.rot / Bconst + 1) * self.B.scale))
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return util.ceil(self.B.clean / ((util.csqrt(lenP) * (util.ceil(self.rot / Bconst) + 2) - 1) * self.B.scale))

    def P(self, keyswitch, omega, logq, K=100):
        if self.const == 0:
            Bconst = 1
        else:
            Bconst = self.B.const

        logw = lambda x: util.clog(x, omega)
        xi = (self.sum * Bconst)**2

        if keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        qLneg3 = 1
        for bits in logq[:-2]:
            qLneg3 *= util.genprime(2**bits, self.B.m, True)
        pLneg2 = util.genprime(2**logq[-2], self.B.m, True)
        qLneg2 = qLneg3 * pLneg2

        if self.rot == 0:
            if keyswitch == 'GHS':
                return util.ceil(K * qLneg3 * self.B.switch / self.B.scale)
            elif keyswitch == 'GHS-RNS':
                return util.ceil(K * qLneg3 * util.csqrt(self.mul) * self.B.switch / self.B.scale)
            elif keyswitch == 'Hybrid':
                return util.ceil(K * omega * util.csqrt(logw(qLneg2)) * self.B.switch / self.B.scale)
            else: # keyswitch == 'Hybrid-RNS'
                return util.ceil(K * pLneg2**util.ceil(self.mul / omega) * util.csqrt(omega * self.mul) * self.B.switch / self.B.scale)
        else:
            if keyswitch == 'GHS':
                return util.ceil(K * qLneg2 * self.B.switch / self.B.scale)
            elif keyswitch == 'GHS-RNS':
                return util.ceil(K * qLneg2 * util.csqrt(self.mul) * self.B.switch / self.B.scale)
            elif keyswitch == 'Hybrid':
                return util.ceil(K * omega * util.csqrt(logw(qLneg2)) * self.B.switch / self.B.scale)
            else: # keyswitch == 'Hybrid-RNS'
                return util.ceil(K * pLneg2**util.ceil(self.mul / omega) * util.csqrt(omega * self.mul) * self.B.switch / self.B.scale)


def genqP(m, t, M, keyswitch, omega, bits=64):
    genp = lambda x: util.flog(x(keyswitch, omega))

    mul = M.mul - 1
    if keyswitch == 'BV-RNS':
        mul = 2 * mul + 2

    logq = [genp(M.first)]
    logq.append(genp(M.middle))
    for _ in range(mul):
        logq.append(genp(M.middle))
    logq.append(genp(M.last))

    for i in range(20):  
        logP = util.flog(M.P(keyswitch, omega, logq))
        P = util.genprime(2**logP, m, False)
        genp = lambda x: util.flog(x(keyswitch, omega, P))

        logq = [genp(M.first)]
        logq.append(genp(M.middle))
        for _ in range(mul):
            logq.append(genp(M.middle))
        logq.append(genp(M.last))

    return logq, logP


def genm(sec, t, logt, secret, Bargs, Margs, qPargs, pow2=True):
    m = 4
    gent = True if not t else False

    while True:
        if gent:
            t = util.genprime(2**(logt - 1), m, batch)
        B = Bounds(m, t, *Bargs)
        M = Mods(B, *Margs)

        logq, logP = genqP(m, t, M, *qPargs)
        est = util.estsecurity(m, sum(logq) + logP, secret)

        if est > sec:
            break

        m <<= 1

    if pow2:
        return m

    raise NotImplementedError("pow2 == False")


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
    sums   = interactive.getsums()
    lib   = interactive.getlib()

    batch     = False
    keyswitch = 'Hybrid'
    omega     = 3
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

        if keyswitch in ['BV', 'BV-RNS', 'Hybrid', 'Hybrid-RNS']:
            omega = interactive.getomega(keyswitch)

    Ve = sigma * sigma
    Vs = { 'Ternary': 2/3, 'Error': Ve }[secret]

    if not m:
        m = genm(sec, t, logt, secret, (Vs, Ve, D), (muls, const, rots, sums), (keyswitch, omega))
    if not t:
        t = util.genprime(2**(logt - 1), m, batch)
    B = Bounds(m, t, Vs, Ve, D)
    M = Mods(B, muls, const, rots, sums)

    logq, logP = genqP(m, t, M, keyswitch, omega)
    sec = max(util.estsecurity(m, sum(logq) + logP, secret), 0)

    if lib == 'PALISADE' and t % m != 1:
        raise ValueError("PALISADE requires t % m == 1")
    interactive.config(sec, m, t, logq, logP, lib)

    if lib == 'PALISADE':
        interactive.writelib(lib)
        if logP > 60:
            interactive.warnlogP()

        logql = max(logq[1], logq[-1])
        codegen.writepalisade(m, t, logq[0], logql, (muls, const, rots, sums), keyswitch, omega, secret)
