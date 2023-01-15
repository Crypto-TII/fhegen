import bgv
import codegen
import math
import util


def config(sec, m, t, logq, logP=None, lib=None):
    print((
        "\nGenerated your BGV configuration!\n"
       f"sec:   {sec}\n"
       f"d:     {util.phi(m)}\n"
       f"t:     {t}\n"
       f"qbits: {sum(logq)} ({logq[0]}, {logq[1]}, {logq[-1]})"))
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

    if lib == 'PALISADE':
        return True

    r = input("Do you want to use full batching with your plaintext modulus? [N/y]: ").lower()

    while True:
        if r in ['', 'n', 'no']:
            return False
        elif r in ['y', 'ye', 'yes']:
            return True

        print("Invalid choice. Possible options are No (default), Yes.")
        r = input("Your choice: ").lower()


def getkeyswitch(lib, default=False):
    if default:
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
        elif r == 'palisade':
            return 'PALISADE'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: No (default), PALISADE.")
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


def getmuls():
    r = input("How many multiplications do you want to perform? [2]: ")

    while True:
        if r == '':
            return 2
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 2).")
        r = input("Your choice: ")


def getomega(keyswitch, default=False):
    if default:
        return 4

    r = input(f"Choose your omega for {keyswitch} key switching [4]: ")

    while True:
        if r == '':
            return 4
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 4).")
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


def getsecret(lib, default=False):
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
        r = input("How many bits do you want at least for the plaintext modulus? [4/?]: ").lower()

        while t is None and logt is None:
            if r == '':
                logt = 4
                break
            elif r.isdigit() and int(r) >= 2:
                logt = int(r)
                break
            elif r != '?':
                print("Invalid choice. ", end='')

            print("Please enter an integer >= 2 (default 16).")
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

    if setadvanced():
        print()
        batch = fullbatch(lib)
        secret = getsecret(lib)
        keyswitch = getkeyswitch(lib)

        if keyswitch in ['BV', 'BV-RNS', 'Hybrid', 'Hybrid-RNS']:
            omega = getomega(keyswitch)
        else:
            omega = 1
    else:
        batch = fullbatch(default=True)
        secret = getsecret(default=True)
        keyswitch = getkeyswitch(default=True)
        omega = getomega(default=True)

    D = 6
    sigma = 3.19
    Ve = sigma * sigma
    Vs = {'Ternary': 2 / 3, 'Error': Ve}[secret]

    if not m:
        m = bgv.genm(sec, t, logt, secret, (Vs, Ve, D), (muls, const, rots, sums), (keyswitch, omega))
    if not t:
        t = util.genprime(2**(logt - 1), m, batch)
    B = bgv.Bounds(m, t, Vs, Ve, D)
    M = bgv.Mods(B, muls, const, rots, sums)

    logq, logP = bgv.genqP(m, t, M, keyswitch, omega)
    sec = max(util.estsecurity(m, sum(logq) + logP, secret), 0)

    if lib == 'PALISADE' and t % m != 1:
        raise ValueError("PALISADE requires t % m == 1")
    config(sec, m, t, logq, logP, lib)

    if lib == 'PALISADE':
        writelib(lib)
        logql = max(logq[1], logq[-1])
        codegen.writepalisade(m, t, logq[0], logql, (muls, const, rots, sums), keyswitch, omega, secret)


if __name__ == "__main__":
    main()
