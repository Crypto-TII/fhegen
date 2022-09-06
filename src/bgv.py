import codegen
import config
import interactive
import math
import util


class Bounds:
    def __init__(self, m, t, Vs, Ve=3.2**2, D=6):
        d = util.phi(m)

        self.clean  = D * t * math.sqrt(d * (1/12 + 2 * d * Vs * Ve + Ve))
        self.switch = D * t * d * math.sqrt(Ve / 12)
        self.scale  = D * t * math.sqrt(d / 12 * (1 + d * Vs))
        self.const  = D * t * math.sqrt(d / 12)


class Mods:
    def __init__(self, B, mul, const, rot, sum, bits=64):
        self.B = B
        self.mul = mul
        self.const = const
        self.rot = rot
        self.sum = sum
        self.bits = bits

    def first(self, keyswitch, omega, P=1):
        logw = lambda x: math.log(x, omega)
        xi = (self.sum * self.B.const)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = math.ceil(math.log(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return 8 * xi * self.B.scale**2
            elif keyswitch == 'BV-RNS':
                return 8 * xi * (self.B.scale + math.sqrt(self.mul) * self.B.switch)**2
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return 8 * lenP * xi * self.B.scale**2
        else:
            if keyswitch == 'BV':
                return 2 * self.sum**2 * (4 * self.rot * omega * math.sqrt(self.mul) * logw(self.B.switch) * self.B.switch + self.B.const * self.B.scale)**2
            elif keyswitch == 'BV-RNS':
                return 32 * self.sum**2 * self.rot**2 * (2 * self.mul + 1) * self.B.switch**2
            elif keyswitch in ['GHS', 'Hybrid']:
                return 8 * self.sum**2 * (self.rot + self.B.const)**2 * self.B.scale**2
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                return 8 * lenP * self.sum**2 * (self.rot + self.B.const)**2 * self.B.scale**2

    def middle(self, keyswitch, omega, P=1):
        logw = lambda x: math.log(x, omega)
        xi = (self.sum * self.B.const)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = math.ceil(math.log(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return 4 * xi * self.B.scale
            elif keyswitch == 'BV-RNS':
                return 4 * xi * (self.B.scale + math.sqrt(self.mul) * self.B.switch)
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return 4 * xi * math.sqrt(lenP) * self.B.scale
        else:
            if keyswitch == 'BV':
                return self.sum**2 * (4 * self.rot * omega * math.sqrt(self.mul) * logw(self.B.switch) * self.B.switch + self.B.const * self.B.scale)
            elif keyswitch == 'BV-RNS':
                return 4 * self.sum**2 * self.rot * math.sqrt(self.mul) * self.B.const * self.B.switch
            elif keyswitch in ['GHS', 'Hybrid']:
                return 4 * self.sum**2 * (self.rot + self.B.const) * self.B.const * self.B.scale
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
                return 4 * self.sum**2 * math.sqrt(lenP) * (self.rot + self.B.const) * self.B.const * self.B.scale

    def last(self, keyswitch, omega, P=1):
        logw = lambda x: math.log(x, omega)
        xi = (self.sum * self.B.const)**2

        if keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['BV', 'BV-RNS', 'GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if keyswitch.endswith('RNS'):
            lenP = math.ceil(math.log(P, 2) / self.bits)
        else:
            lenP = 1

        if self.rot == 0:
            if keyswitch in ['BV', 'GHS', 'Hybrid']:
                return self.B.clean / self.B.scale
            elif keyswitch == 'BV-RNS':
                return self.B.clean / (self.B.scale + 2 * math.sqrt(self.mul) * self.B.switch)
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return self.B.clean / ((2 * math.sqrt(lenP) - 1) * self.B.scale)
        else:
            if keyswitch == 'BV':
                return self.B.clean / (2 * self.rot * omega * math.sqrt(self.mul) * logw(self.B.switch) * self.B.switch / self.B.const - self.B.scale / 2)
            elif keyswitch == 'BV-RNS':
                return self.B.clean / (16 * self.sum**2 * self.rot**2 * self.mul * self.B.switch**2 - self.B.scale)
            elif keyswitch in ['GHS', 'Hybrid']:
                return self.B.clean / ((self.rot / self.B.const + 1) * self.B.scale)
            else: # keyswitch in ['GHS-RNS', 'Hybrid-RNS']
                return self.B.clean / ((math.sqrt(lenP) * (self.rot / self.B.const + 2) - 1) * self.B.scale)

    def P(self, keyswitch, omega, qlast, K=100):
        logw = lambda x: math.log(x, omega)
        xi = (self.sum * self.B.const)**2

        if keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']:
            raise ValueError("keyswitch not in ['GHS', 'GHS-RNS', 'Hybrid', 'Hybrid-RNS']")

        if self.rot == 0:
            if keyswitch == 'GHS':
                return K * qlast * self.B.switch / self.B.scale
            elif keyswitch == 'GHS-RNS':
                return K * qlast * math.sqrt(self.mul) * self.B.switch / self.B.scale
            elif keyswitch == 'Hybrid':
                return K * omega * math.sqrt(logw(qlast)) * self.B.switch / self.B.scale
            else: # keyswitch == 'Hybrid-RNS'
                return 4 * K * xi * math.sqrt(K * self.mul) * self.B.switch
        else:
            if keyswitch == 'GHS':
                return K * qlast * self.B.switch / self.B.scale
            elif keyswitch == 'GHS-RNS':
                return K * qlast * math.sqrt(self.mul) * self.B.switch / self.B.scale
            elif keyswitch == 'Hybrid':
                return K * omega * math.sqrt(logw(qlast)) * self.B.switch / self.B.scale
            else: # keyswitch == 'Hybrid-RNS'
                return 4 * K * self.sum**2 * (self.rot + self.B.const) * math.sqrt(K * self.mul) * self.B.const * self.B.switch


def genqP(m, t, M, keyswitch, omega, bits=64):
    genp = lambda x: util.flog2(x(keyswitch, omega))

    mul = M.mul
    if keyswitch == 'BV-RNS':
        mul = 2 * mul + 1

    logq = [genp(M.first)]
    logq.append(genp(M.middle))
    for _ in range(mul):
        logq.append(genp(M.middle))
    logq.append(genp(M.last))

    qlast = util.genprime(2**logq[-1], m, True)
    logP = util.flog2(M.P(keyswitch, omega, qlast))
    P = util.genprime(2**logP, m, False)
    genp = lambda x: util.flog2(x(keyswitch, omega, P))

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
