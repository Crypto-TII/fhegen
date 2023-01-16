import math
import util


class Bounds:
    def __init__(self, m, t, Vs, Ve, D):
        d = util.phi(m)
        self.m = m
        self.t = t
        self.Vs = Vs
        self.Ve = Ve
        self.D = D

        self.clean = D * t * math.sqrt(d * (1 / 12 + 2 * d * Vs * Ve + Ve))
        self.switch = D * t * d * math.sqrt(Ve / 12)
        self.scale = D * t * math.sqrt(d / 12 * (1 + d * Vs))
        self.const = D * t * math.sqrt(d / 12)


class Mods:
    def __init__(self, B, mul, const, rot, sum, keyswitch, omega, bits=64):
        self.mul = mul
        self.const = const
        self.rot = rot
        self.sum = sum
        self.keyswitch = keyswitch
        self.bits = bits
        self.omega = omega

        self.B = B
        self.update(B.m, B.t)

    def _lenP(self, P=1):
        if P is not None and self.keyswitch.endswith('RNS'):
            return max(util.ceil(math.log2(P) / self.bits), 1)
        else:
            return 1

    def update(self, m, t):
        self.B = Bounds(m, t, self.B.Vs, self.B.Ve, self.B.D)
        self.Bclean = self.B.clean
        self.Bswitch = self.B.switch
        self.Bscale = self.B.scale
        self.Bconst = 1 if self.const == 0 else self.B.const
        self.depth = 2 * (self.mul + 1) if self.keyswitch == 'BV' and self.rot != 0 else self.mul + 1
        self.xi = (self.sum * self.Bconst)**2

    def first(self, P):
        factor = 1
        if self.rot == 0:
            factor = 8 * self.xi
        else:
            factor = 8 * self.sum**2
        if self.keyswitch == 'BV' and self.rot != 0:
            factor *= 4 * (self.depth - 1)
        if self.keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
            factor *= self._lenP(P)

        B = 1
        if self.keyswitch == 'BV-RNS' and self.rot == 0:
            B = self.Bscale + math.sqrt(self.depth - 1) * self.Bswitch
        elif self.keyswitch == 'BV-RNS' and self.rot != 0:
            B = self.Bswitch
        elif self.keyswitch == 'BV' and self.rot != 0:
            B = 2 * self.rot * self.omega * math.sqrt(self.depth - 1)
            B *= math.log(self.Bswitch, self.omega) * self.Bswitch
            B += self.Bconst * self.Bscale
        elif self.rot != 0:
            B = (self.rot + self.Bconst) * self.Bscale
        else:
            B = self.Bscale

        B = factor * B**2
        return util.ceil(math.log2(B)) if B > 1 else 0

    def middle(self, P=1):
        factor = 1
        if self.rot == 0:
            factor = 4 * self.xi
        else:
            factor = 4 * self.sum
        if self.keyswitch == 'BV' and self.rot != 0:
            factor /= 4
        if self.keyswitch in ['GHS-RNS', 'Hybrid-RNS']:
            factor *= math.sqrt(self._lenP(P))

        B = 1
        if self.keyswitch == 'BV-RNS' and self.rot == 0:
            B = self.Bscale + math.sqrt(self.depth - 1) * self.Bswitch
        elif self.keyswitch == 'BV-RNS' and self.rot != 0:
            B = self.rot * math.sqrt(self.depth - 1) * self.Bconst * self.Bswitch
        elif self.keyswitch == 'BV' and self.rot != 0:
            B = 4 * self.rot * self.omega * math.sqrt(self.depth - 1)
            B *= math.log(self.Bswitch, self.omega) * self.Bswitch
            B += self.Bconst * self.Bscale
            B *= self.Bconst
        elif self.rot == 0:
            B = self.Bscale
        else:
            B = (self.rot + self.Bconst) * self.Bconst * self.Bscale

        B = factor * B
        return util.ceil(math.log2(B)) if B > 1 else 0

    def last(self, P=1):
        num = self.Bclean
        if self.keyswitch == 'BV' and self.rot != 0:
            num *= self.Bconst

        div = self.Bscale
        if self.keyswitch == 'BV-RNS' and self.rot == 0:
            div += 2 * math.sqrt(self.depth - 1) * self.Bswitch
        elif self.keyswitch == 'BV-RNS' and self.rot != 0:
            div = 16 * self.sum**2 * self.rot**2 * (self.depth - 1)
            div = div * self.Bswitch**2 - self.Bscale
        elif self.keyswitch == 'BV' and self.rot != 0:
            div = 2 * self.rot * self.omega * math.sqrt(self.depth - 1)
            div *= math.log(self.Bswitch, self.omega) * self.Bswitch
        elif self.keyswitch in ['GHS-RNS', 'Hybrid-RNS'] and self.rot == 0:
            div *= 2 * math.sqrt(self._lenP(P)) - 1
        elif self.keyswitch in ['GHS-RNS', 'Hybrid-RNS'] and self.rot != 0:
            div *= math.sqrt(self._lenP(P)) * ((self.rot / self.Bconst + 2) - 1)
        elif self.keyswitch in ['GHS', 'Hybrid'] and self.rot != 0:
            div *= self.rot / self.Bconst + 1

        B = num / div
        return util.ceil(math.log2(B)) if B > 1 else 0

    def switch(self, logq, K=100):
        qLneg3 = 2**(sum(logq[:-2]) - len(logq[:-2]))
        pLneg2 = 2**(logq[-2] - 1)
        qLneg2 = qLneg3 * pLneg2

        factor = 1
        if self.keyswitch in ['GHS', 'GHS-RNS'] and self.rot == 0:
            factor = K * qLneg3
        elif self.keyswitch in ['GHS', 'GHS-RNS'] and self.rot != 0:
            factor = K * qLneg2
        else:
            factor = K
        if self.keyswitch == 'GHS-RNS' and self.rot == 0:
            factor *= math.sqrt(self.depth - 2)
        if self.keyswitch == 'GHS-RNS' and self.rot != 0:
            factor *= math.sqrt(self.depth - 1)
        if self.keyswitch == 'Hybrid-RNS':
            factor *= pLneg2**util.ceil(self.depth / self.omega)
            factor *= math.sqrt(self.omega * (self.depth - 1))
        if self.keyswitch == 'Hybrid':
            factor *= self.omega * math.sqrt(math.log(qLneg2, self.omega))

        B = factor * util.ceil(self.Bswitch) // util.ceil(self.Bscale)
        return util.ceil(math.log2(B)) if B > 1 else 0
