import math
import util


def config(sec, m, t, q, logP=None, lib=None):
    logq  = util.flog2(int(math.prod(q)))
    logq0 = util.flog2(q[0])
    logql = util.flog2(q[1])
    logqL = util.flog2(q[-1])

    print((
        "\nGenerated your BGV configuration!\n"
       f"sec:   {sec:.2f}\n"
       f"d:     {util.phi(m)}\n"
       f"t:     {t}\n"
       f"logq:  {logq} ({logq0}, {logql}, {logqL})"))
    if logP:
        print(f"logP:  {logP}")
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


def fullbatch(lib):
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


def getkeyswitch(lib):
    r = input("Which key switching method do you prefer? [Hybrid/?]: ").lower()

    while True:
        if r == '' or 'hybrid'.startswith(r):
            return 'Hybrid'
        elif r == 'bv':
            return 'BV'
        elif r == 'ghs':
            return 'GHS'
        elif r != '?':
            print("Invalid choice. ", end='')

        print("Possible options are: Hybrid (default), BV, GHS.")
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


def getomega(keyswitch):
    r = input(f"Choose your omega for {keyswitch} key switching [4]: ")

    while True:
        if r == '':
            return 4
        elif r.isdigit() and int(r) > 0:
            return int(r)

        print("Invalid choice. Please enter an integer > 0 (default 4).")
        r = input("Your choice: ")


def getrots():
    r = input(f"How many rotations do you want to perform? [0]: ")

    while True:
        if r == '':
            return 0
        elif r.isdigit() and int(r) >= 0:
            return int(r)

        print("Invalid choice. Please enter an integer >= 0 (default 0).")
        r = input("Your choice: ")


def getsecret(lib):
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

    if t == None:
        r = input("How many bits do you want at least for the plaintext modulus? [16/?]: ").lower()

        while t == None and logt == None:
            if r == '':
                logt = 16
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


def warnlogP():
    print((
        "Warning: PALISADE does not support logP > 60. "
        "However, due to the heuristic approach to generating the parameters, "
        "they might still work. You can run our example (make && ./a.out) "
        "for a first impression."))


def welcome():
    print("Welcome to the interactive parameter generator for BGV! :)\n")


def writelib(lib):
    print(f"Generating Makefile, main.cpp and bench.cpp for {lib}.")
