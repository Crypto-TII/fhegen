import bfv
import bgv
import codegen
import math
import util


def pconfig(scheme, model, sec, m, t, logq, logP=None, lib=None):
    print((
        f"\nGenerated your {scheme} configuration!\n"
        f"model: {model}\n"
        f"sec:   {sec}\n"
        f"d:     {util.phi(m)}\n"
        f"t:     {t}"))

    if len(logq) > 1:
        print(f"qbits: {sum(logq)} ({logq[0]}, {logq[1]}, {logq[-1]})")
    else:
        print(f"qbits: {logq[0]}")

    if logP:
        print(f"Pbits: {logP}")
    if lib:
        print(f"slots: {util.slots(m, t)}")


def doconst():
    r = input("Do you want to perform a constant multiplication? [N/y]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            return False
        elif r in ['y', 'ye', 'yes']:
            return True

        print("Invalid choice. Possible options are No (default), Yes.")
        r = input("Your choice: ").lower()


def fullbatch(lib, default=False):
    if default:
        return False

    r = input("Do you want to use full batching with your plaintext modulus? [N/y]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            return False
        elif r in ['y', 'ye', 'yes']:
            return True

        print("Invalid choice. Possible options are No (default), Yes.")
        r = input("Your choice: ").lower()


def getbeta(lib, keyswitch, default=False):
    if default or lib:
        return 2**10

    r = input(f"Choose your beta for {keyswitch} key switching [2^10]: ")

    while True:
        if r == '':
            return 2**10
        elif r.isdigit() and int(r) > 1:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 2^10).")
        r = input("Your choice: ")


def getkeyswitch(lib, default=False):
    if default or lib:
        return 'Hybrid-RNS'

    r = input("Which key switching method do you prefer? [Hybrid-RNS/?]: ").lower()

    while True:
        if r == '' or 'hybrid-rns'.startswith(r):
            return 'Hybrid-RNS'
        elif r == 'bv':
            return 'BV'
        elif r == 'bv-rns':
            return 'BV-RNS'
        elif r == 'ghs':
            return 'GHS'
        elif r == 'ghs-rns':
            return 'GHS-RNS'
        elif 'hybrid'.startswith(r):
            return 'Hybrid'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: BV, BV-RNS, GHS, GHS-RNS, Hybrid, Hybrid-RNS (default).")
        r = input("Your choice: ").lower()


def getlib():
    r = input("Do you want to use a specific library? [N/?]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            return None
        elif r == 'openfhe':
            return 'OpenFHE'
        elif r == 'palisade':
            return 'PALISADE'
        elif r == 'seal':
            return 'SEAL'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: No (default), OpenFHE, PALISADE, SEAL.")
        r = input("Your choice: ").lower()


def getm():
    r = input("Input your cyclotomic order [1024]: ")

    while True:
        if r == '':
            return 1024
        elif r.isdigit() and int(r) >= 4:
            return int(r)

        print("Invalid choice. Please enter an integer >= 4 (default 1024).")
        r = input("Your choice: ")


def getmodel():
    r = input("Which circuit model do you want to use? [Base]: ").lower()

    while True:
        if r == '' or 'base'.startswith(r):
            return 'Base'
        elif r == '1' or 'model1'.startswith(r):
            return 'Model1'
        elif r == '2' or 'model2'.startswith(r):
            return 'Model2'
        elif 'openfhe'.startswith(r):
            return 'OpenFHE'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: Base (default), Model1, Model2, OpenFHE.")
        r = input("Your choice: ").lower()


def getmuls():
    r = input("How many multiplications do you want to perform? [2]: ")

    while True:
        if r == '':
            return 2
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 2).")
        r = input("Your choice: ")


def getomega(lib, keyswitch, default=False):
    if default or lib:
        return 3

    r = input(f"Choose your omega for {keyswitch} key switching [3]: ")

    while True:
        if r == '':
            return 3
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 3).")
        r = input("Your choice: ")


def getrots():
    r = input("How many rotations do you want to perform? [0]: ")

    while True:
        if r == '':
            return 0
        elif r.isdigit() and int(r) >= 0:
            return int(r)

        print("Invalid choice. Please enter an integer >= 0 (default 0).")
        r = input("Your choice: ")


def getscheme():
    r = input("Which scheme do you want to generate paramters for? [BGV/?]: ").lower()

    while True:
        if r == '' or 'bgv'.startswith(r):
            return 'BGV'
        elif 'bfv'.startswith(r):
            return 'BFV'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: BGV (default), BFV.")
        r = input("Your choice: ").lower()


def getsdist(lib, default=False):
    if default:
        return 'Ternary'

    r = input("Choose your secret distribution [Ternary/?]: ").lower()

    while True:
        if r == '' or 'ternary'.startswith(r):
            return 'Ternary'
        elif 'error'.startswith(r):
            return 'Error'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: Ternary (default), Error.")
        r = input("Your choice: ").lower()


def getsecurity():
    r = input("Choose your security level [128]: ")

    while True:
        if r == '':
            return 128
        elif r.isdigit() and int(r) >= 40:
            return int(r)

        print("Invalid choice. Please enter an integer > 40 (default 128).")
        r = input("Your choice: ")


def getsums():
    r = input("What is the maximum number of summands between each multiplication? [1]: ")

    while True:
        if r == '':
            return 1
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 1).")
        r = input("Your choice: ")


def gett():
    t, logt = None, None
    r = input("Do you want a specific plaintext modulus? [N/?]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            break
        elif r.isdigit() and int(r) >= 2:
            t = int(r)
            break
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Please enter No (default) or an integer >= 2.")
        r = input("Your choice: ").lower()

    if t is None:
        r = input("How many bits do you want at least for the plaintext modulus? [17/?]: ").lower()

        while t is None and logt is None:
            if r == '':
                logt = 17
                break
            elif r.isdigit() and int(r) >= 2:
                logt = int(r)
                break
            elif r != '?':
                print("Invalid choice. ", end='')

            print("Please enter an integer >= 2 (default 17).")
            r = input("Your choice: ").lower()
    else:
        logt = math.floor(math.log2(t))

    return t, logt


def setadvanced():
    r = input("Do you want to continue to the advanced settings? [N/y]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            return False
        elif r in ['y', 'ye', 'yes']:
            return True

        print("Invalid choice. Possible options are No (default), Yes.")
        r = input("Your choice: ").lower()


def setsecurity(secdef, t):
    if t == 2:
        return False

    r = input(f"Do you want to set the security level or choose a cyclotomic order? [{secdef}]: ").lower()

    while True:
        if r == '':
            return secdef.startswith('Security')
        elif 'security'.startswith(r):
            return True
        elif 'order'.startswith(r):
            return False

        print("Invalid choice. Possible options are Security (default) or order.")
        r = input("Your choice: ").lower()


def usepow2():
    return True


def welcome():
    print("Welcome to the interactive parameter generator! :)\n")


def writelib(lib):
    print(f"Generating an example using your configuration for {lib}.")


def main():
    welcome()
    schemename = getscheme()
    if schemename == 'BGV':
        scheme = bgv
    elif schemename == 'BFV':
        scheme = bfv
    model = getmodel()

    t, logt = gett()
    secdef = 'Order/security' if t else 'Security/order'

    if setsecurity(secdef, t):
        m, sec = None, getsecurity()
        pow2 = usepow2()
    else:
        m, sec = getm(), None
    print()

    muls = getmuls()
    const = doconst()
    rots = getrots()
    sums = getsums()
    lib = getlib()

    batch = fullbatch(lib, default=True)
    sdist = getsdist(lib, default=True)
    keyswitch = getkeyswitch(lib, default=True)
    omega = getomega(lib, keyswitch, default=True)
    beta = getbeta(lib, keyswitch, default=True)

    if setadvanced():
        print()
        batch = fullbatch(lib)
        sdist = getsdist(lib)
        keyswitch = getkeyswitch(lib)

        if keyswitch in ['BV', 'BV-RNS', 'Hybrid']:
            beta = getbeta(lib, keyswitch)
        if keyswitch in ['Hybrid-RNS']:
            omega = getomega(lib, keyswitch)

    sigma = 3.19
    Ve = sigma * sigma
    Vs = {'Ternary': 2 / 3, 'Error': Ve}[sdist]

    genm = False
    if not m:
        genm = True
        m = 4

    gent = False
    if not t:
        gent = True
        t = util.gent(m, gent, t, logt, batch)

    ops = {'model': model, 'muls': muls, 'const': const, 'rots': rots, 'sums': sums}
    targs = {'gen': gent, 't': t, 'logt': logt, 'batch': batch}
    Bargs = {'m': m, 't': t, 'D': 6, 'Vs': Vs, 'Ve': Ve}
    kswargs = {'method': keyswitch, 'L': muls + 1, 'beta': beta, 'omega': omega}

    if genm:
        if not pow2:
            raise NotImplementedError("pow2 == False")

        while True:
            logq, logP = scheme.logqP(ops, Bargs, kswargs, sdist)
            log = sum(logq) + logP if logP else sum(logq)
            if logP and util.estsecurity(m, log, sdist) > sec:
                break

            m <<= 1
            Bargs['m'] = m

            t = util.gent(m, **targs)
            targs['t'] = t
            Bargs['t'] = t
    else:
        logq, logP = scheme.logqP(ops, Bargs, kswargs, sdist)

    sec = util.estsecurity(m, sum(logq) + logP, sdist)
    pconfig(schemename, model, sec, m, t, logq, logP, lib)

    if lib == 'OpenFHE':
        if schemename == 'BGV':
            q0bits = logq[0]
            qlbits = logq[1]
        else:  # schemename == 'BFV'
            q0bits = math.ceil(logq[0] / muls)
            qlbits = math.ceil(logq[0] / muls)

        writelib(lib)
        codegen.openfhe({
            'scheme': schemename,
            'd': util.phi(m),
            't': t,
            'sdist': {'Ternary': 'UNIFORM_TERNARY', 'Error': 'GAUSSIAN'}[sdist],
            'depth': muls + 1,
            'q0bits': q0bits,
            'qlbits': qlbits,
            'slots': util.slots(m, t),
        })
    if lib == 'PALISADE':
        if schemename == 'BGV':
            q0bits = logq[0]
            qlbits = logq[1]
        else:  # schemename == 'BFV'
            q0bits = math.ceil(logq[0] / muls)
            qlbits = math.ceil(logq[0] / muls)

        writelib(lib)
        codegen.palisade({
            'scheme': schemename,
            'sigma': sigma,
            'd': util.phi(m),
            't': t,
            'sdist': {'Ternary': 'OPTIMIZED', 'Error': 'RLWE'}[sdist],
            'depth': muls + 1,
            'q0bits': q0bits,
            'qlbits': qlbits,
            'slots': util.slots(m, t),
            'rots': rots,
            'sums': sums,
        })
    if lib == 'SEAL':
        if schemename == 'BGV':
            q0bits = logq[0]
            qlbits = logq[1]
            qMbits = logq[-1]
        else:  # schemename == 'BFV'
            q0bits = math.ceil(logq[0] / muls)
            qlbits = math.ceil(logq[0] / muls)

        q = []
        for i in range(muls):
            if i == 0:
                q.append(util.genprime(1 << q0bits, m, batch))
            if i == 1:
                start = q[-1] if q0bits == qlbits else 1 << qlbits
                q.append(util.genprime(start, m, batch))

        if schemename == 'BGV':
            if qMbits == qlbits:
                start = q[-1]
            elif qMbits == q0bits:
                start = q[0]
            else:
                start = 1 << qMbits
            q.append(util.genprime(start, m, batch))

        writelib(lib)
        codegen.seal({
            'scheme': schemename,
            'd': util.phi(m),
            'q': q,
            't': t,
        })


if __name__ == "__main__":
    main()
