import codegen
import interactive
import math
import util


ksw = ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']


class Bounds:
    def __init__(self, m, t, Vs, Ve=3.2**2, D=6):
        d = util.phi(m)

        self.m = m
        self.clean = D * t * math.sqrt(d * (1 / 12 + 2 * d * Vs * Ve + Ve))
        self.switch = D * t * d * math.sqrt(Ve / 12)
        self.scale = D * t * math.sqrt(d / 12 * (1 + d * Vs))
        self.const = D * t * math.sqrt(d / 12)


class Mods:
    def __init__(self, B, mul, const, rot, sum, bits=64):
        self.B = B
        self.mul = mul
        self.const = const
        self.rot = rot
        self.sum = sum
        self.bits = bits

    def first(self, keyswitch, omega, P=1):
        if keyswitch not in ksw:
            raise ValueError(f"keyswitch not in {ksw}")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(math.log2(P) / self.bits)
        lenP = max(lenP, 1)
        Bconst = 1 if self.const == 0 else self.B.const
        xi = (self.sum * Bconst)**2

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                ret = 8 * xi * self.B.scale**2
            elif keyswitch == 'BV-RNS':
                ret = 8 * xi * (self.B.scale + math.sqrt(self.mul) * self.B.switch)**2
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                ret = 8 * lenP * xi * self.B.scale**2
        else:
            if keyswitch == 'BV':
                ret = 8 * self.sum**2 * (2 * self.rot * omega * math.sqrt(self.mul) * math.log(self.B.switch, omega) * self.B.switch + Bconst * self.B.scale)**2
            elif keyswitch == 'BV-RNS':
                ret = 32 * self.sum**2 * self.rot**2 * (2 * self.mul + 1) * self.B.switch**2
            elif keyswitch in ['GHS', 'Hybrid']:
                ret = 8 * self.sum**2 * (self.rot + Bconst)**2 * self.B.scale**2
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                ret = 8 * lenP * self.sum**2 * (self.rot + Bconst)**2 * self.B.scale**2

        return util.ceil(math.log2(ret)) if ret > 1 else 0

    def middle(self, keyswitch, omega, P=1):
        if keyswitch not in ksw:
            raise ValueError(f"keyswitch not in {ksw}")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(math.log2(P) / self.bits)
        lenP = max(lenP, 1)
        Bconst = 1 if self.const == 0 else self.B.const
        xi = (self.sum * Bconst)**2

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                ret = 4 * xi * self.B.scale
            elif keyswitch == 'BV-RNS':
                ret = 4 * xi * (self.B.scale + math.sqrt(self.mul) * self.B.switch)
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return 4 * xi * math.sqrt(lenP) * self.B.scale
        else:
            if keyswitch == 'BV':
                ret = self.sum**2 * Bconst * (4 * self.rot * omega * math.sqrt(self.mul) * math.log(self.B.switch, omega) * self.B.switch + Bconst * self.B.scale)
            elif keyswitch == 'BV-RNS':
                ret = 4 * self.sum**2 * self.rot * math.sqrt(self.mul) * Bconst * self.B.switch
            elif keyswitch in ['GHS', 'Hybrid']:
                ret = 4 * self.sum**2 * (self.rot + Bconst) * Bconst * self.B.scale
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                ret = 4 * self.sum**2 * math.sqrt(lenP) * (self.rot + Bconst) * Bconst * self.B.scale

        return util.ceil(math.log2(ret)) if ret > 1 else 0

    def last(self, keyswitch, omega, P=1):
        if keyswitch not in ksw:
            raise ValueError(f"keyswitch not in {ksw}")

        if keyswitch.endswith('RNS'):
            lenP = util.ceil(math.log2(P) / self.bits)
        lenP = max(lenP, 1)
        Bconst = 1 if self.const == 0 else self.B.const

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                ret = self.B.clean / self.B.scale
            elif keyswitch == 'BV-RNS':
                ret = self.B.clean / (self.B.scale + 2 * math.sqrt(self.mul) * self.B.switch)
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                ret = self.B.clean / ((2 * math.sqrt(lenP) - 1) * self.B.scale)
        else:
            if keyswitch == 'BV':
                ret = self.B.clean * Bconst / (2 * self.rot * omega * math.sqrt(self.mul) * math.log(self.B.switch, omega) * self.B.switch)
            elif keyswitch == 'BV-RNS':
                ret = self.B.clean / (16 * self.sum**2 * self.rot**2 * self.mul * self.B.switch**2 - self.B.scale)
            elif keyswitch in ['GHS', 'Hybrid']:
                ret = self.B.clean / ((self.rot / Bconst + 1) * self.B.scale)
            else:  # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                ret = self.B.clean / ((math.sqrt(lenP) * (self.rot / Bconst + 2) - 1) * self.B.scale)

        return util.ceil(math.log2(ret)) if ret > 1 else 0

    def P(self, keyswitch, omega, logq, K=100):
        if keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        qLneg3 = 2**(sum(logq[:-2]) - len(logq[:-2]))
        pLneg2 = 2**(logq[-2] - 1)
        qLneg2 = qLneg3 * pLneg2

        if self.rot == 0:
            if keyswitch == 'GHS':
                ret = K * qLneg3 * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            elif keyswitch == 'GHS-RNS':
                ret = K * qLneg3 * util.ceil(math.sqrt(self.mul)) * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            elif keyswitch == 'Hybrid':
                ret = K * omega * util.ceil(math.sqrt(math.log(qLneg2, omega))) * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            else:  # keyswitch == 'Hybrid-RNS'
                ret = K * pLneg2**util.ceil(self.mul / omega) * util.ceil(math.sqrt(omega * self.mul)) * util.ceil(self.B.switch) // util.ceil(self.B.scale)
        else:
            if keyswitch == 'GHS':
                ret = K * qLneg2 * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            elif keyswitch == 'GHS-RNS':
                ret = K * qLneg2 * util.ceil(math.sqrt(self.mul)) * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            elif keyswitch == 'Hybrid':
                ret = K * omega * util.ceil(math.sqrt(math.log(qLneg2, omega))) * util.ceil(self.B.switch) // util.ceil(self.B.scale)
            else:  # keyswitch == 'Hybrid-RNS'
                ret = K * pLneg2**util.ceil(self.mul / omega) * util.ceil(math.sqrt(omega * self.mul)) * util.ceil(self.B.switch) // util.ceil(self.B.scale)

        return util.ceil(math.log2(ret)) if ret > 0 else 0


def genqP(m, t, M, keyswitch, omega, bits=64):
    mul = M.mul - 1
    if keyswitch == 'BV-RNS':
        mul = 2 * mul + 2

    logq = [M.first(keyswitch, omega)]
    for _ in range(mul):
        logq.append(M.middle(keyswitch, omega))
    logq.append(M.last(keyswitch, omega))

    for i in range(20):
        logP = M.P(keyswitch, omega, logq)
        logq = [M.first(keyswitch, omega, 2**logP)]
        for _ in range(mul):
            logq.append(M.middle(keyswitch, omega, 2**logP))
        logq.append(M.last(keyswitch, omega, 2**logP))

    return logq, logP


def genm(sec, t, logt, secret, Bargs, Margs, qPargs, pow2=True):
    gent = True if not t else False
    m = 4

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
        pow2 = interactive.usepow2()
    else:
        m, sec = interactive.getm(), None
    print()

    muls = interactive.getmuls()
    const = interactive.doconst()
    rots = interactive.getrots()
    sums = interactive.getsums()
    lib = interactive.getlib()

    batch = False
    keyswitch = 'Hybrid'
    omega = 3
    secret = 'Ternary'
    sigma = 3.2
    D = 6

    if lib == 'PALISADE':
        batch = True

    if interactive.setadvanced():
        print()
        batch = interactive.fullbatch(lib)
        secret = interactive.getsecret(lib)
        keyswitch = interactive.getkeyswitch(lib)

        if keyswitch in ['BV', 'BV-RNS', 'Hybrid', 'Hybrid-RNS']:
            omega = interactive.getomega(keyswitch)

    Ve = sigma * sigma
    Vs = {'Ternary': 2 / 3, 'Error': Ve}[secret]

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
