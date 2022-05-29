import config
import math
import util


def benchloop(body, var):
    return (
        "\tfor (auto _ : state) {\n"
       f"{body}"
       f"\t\tbenchmark::DoNotOptimize({var});\n"
        "\t\tbenchmark::ClobberMemory();\n"
        "\t}\n")


def benchmsg(d, t):
    return (
        "\tstd::random_device dev;\n"
        "\tstd::mt19937 rng(dev());\n"
       f"\tstd::uniform_int_distribution<int64_t> dist(0, {t - 1});\n"
        "\tstd::vector<int64_t> msg;\n"
       f"\tmsg.reserve({d});\n"
       f"\tfor (size_t i = 0; i < {d}; ++i) {{\n"
        "\t\tmsg.push_back(dist(rng));\n"
        "\t}\n")


def maincmp(t, muls, const, rots, sums, slots, centered, n=10):
    if const:
        cmul = f"\n\t\ttmp = (tmp * 2) % {t};\n"
    else:
        cmul = ''

    if centered:
        cmod = (
            "\n\t\t/* compute centered result mod t */\n"
           f"\t\tif (cmp >= {t // 2}) {{\n"
           f"\t\t\tcmp -= {t};\n"
            "\t\t}\n")
    else:
        cmod = ''

    if muls & 1 == 1 and rots & 1 == 1:
        x0, xn = 1, n + 1
    else:
        x0, xn = 0, n

    return (
       f"\tfor (int64_t x = {x0}; x < {xn}; ++x) {{\n"
       f"\t\tint64_t cmp = x % {slots};\n"
       f"\t\tfor (size_t i = 0; i < {muls}; ++i) {{\n"
       f"\t\t\tauto tmp = (cmp * cmp) % {t};\n"
       f"{cmul}"
       f"\t\t\tfor (size_t j = 1; j < {sums}; ++j) {{\n"
       f"\t\t\t\ttmp = (tmp + cmp) % {t};\n"
        "\t\t\t}\n"
        "\t\t\tcmp = tmp;\n"
        "\t\t}\n"
       f"{cmod}"
        "\t\tstd::cout << cmp << \" \";\n"
        "\t}\n")


def mainmsg(t, slots, indent=1):
    return (
        "\n"
        "\tstd::vector<int64_t> msg;\n"
       f"\tmsg.reserve({slots});\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
       f"\t\tmsg.push_back(i % {t});\n"
        "\t}\n\n")


def writemake(incs, libs, clean=''):
    with open('Makefile', 'w+') as f:
        f.write(
            ".PHONY: all bench clean\n\n"
            "all: main.cpp\n"
           f"\tc++ -std=c++17 -g {incs} main.cpp {libs}\n\n"
            "bench: bench.cpp\n"
           f"\tc++ -std=c++17 -march=native -O3 {incs} bench.cpp -lbenchmark {libs}\n\n"
            "clean:\n"
            "\trm -f a.out\n"
           f"{clean}")


def writebench(inc, use, bench):
    ctx, gen, enc, dec, mul, const, rot, add, all = bench

    if const:
        bconst = (
           f"static void\n"
            "BM_MulConst(benchmark::State& state)\n"
            "{\n"
           f"{const}"
            "}\n\n")
        bregister = "BENCHMARK(BM_MulConst)->BENCHCONFIG;\n"
    else:
        bconst = ''
        bregister = ''

    with open('bench.cpp', 'w+') as f:
        f.write(
            "#include <benchmark/benchmark.h>\n"
           f"#include <{inc}>\n"
           f"#include <random>\n"
           f"{use}\n"
           f"#define BENCHCONFIG Repetitions({config.BENCH_REPS})->DisplayAggregatesOnly(true)->Unit(benchmark::kMillisecond)\n\n"
            "static void\n"
            "BM_Context(benchmark::State& state)\n"
            "{\n"
           f"{ctx}"
            "}\n\n"
            "static void\n"
            "BM_KeyGen(benchmark::State& state)\n"
            "{\n"
           f"{gen}"
            "}\n\n"
            "static void\n"
            "BM_Encrypt(benchmark::State& state)\n"
            "{\n"
           f"{enc}"
            "}\n\n"
            "static void\n"
            "BM_Decrypt(benchmark::State& state)\n"
            "{\n"
           f"{dec}"
            "}\n\n"
            "static void\n"
            "BM_Mul(benchmark::State& state)\n"
            "{\n"
           f"{mul}"
            "}\n\n"
           f"{bconst}"
           f"static void\n"
            "BM_Rot(benchmark::State& state)\n"
            "{\n"
           f"{rot}"
            "}\n\n"
            "static void\n"
            "BM_Add(benchmark::State& state)\n"
            "{\n"
           f"{add}"
            "}\n\n"
            "static void\n"
            "BM_Circuit(benchmark::State& state)\n"
            "{\n"
           f"{all}"
            "}\n\n"
            "BENCHMARK(BM_Context)->BENCHCONFIG;\n"
            "BENCHMARK(BM_KeyGen)->BENCHCONFIG;\n"
            "BENCHMARK(BM_Encrypt)->BENCHCONFIG;\n"
            "BENCHMARK(BM_Decrypt)->BENCHCONFIG;\n"
            "BENCHMARK(BM_Mul)->BENCHCONFIG;\n"
           f"{bregister}"
            "BENCHMARK(BM_Rot)->BENCHCONFIG;\n"
            "BENCHMARK(BM_Add)->BENCHCONFIG;\n"
            "BENCHMARK(BM_Circuit)->BENCHCONFIG;\n"
            "BENCHMARK_MAIN();\n")


def writemain(inc, use, main):
    with open('main.cpp', 'w+') as f:
        f.write(
           f"#include <{inc}>\n"
           f"{use}\n"
            "int\n"
            "main(void)\n"
            "{\n"
           f"{main}\n"
            "\treturn 0;\n"
            "}\n")


def writehelib(m, t, logq, logP, ops, keyswitch, omega=4, D=6):
    writemake(config.HELIB_INCS, config.HELIB_LIBS, "\trm -f helib.log\n")

    muls, const, rots, sums = ops

    d = util.phi(m)
    slots = util.slots(m, t)

    if keyswitch == 'GHS':
        w = 1

    if const:
        factor = 2
    else:
        factor = 1

    ctx = lambda tabs: (
       f"{tabs}auto ctx = ContextBuilder<helib::BGV>()\n"
       f"{tabs}\t/* cyclotomic order  */ .m({m})\n"
       f"{tabs}\t/* plaintext modulus */ .p({t})\n"
       f"{tabs}\t/* log2(q)           */ .bits({logq})\n"
       f"{tabs}\t/* log2(P)           */ .bitsInSpecialPrimes({logP})\n"
       f"{tabs}\t/* omega HYBRID      */ .c({omega})\n"
       f"{tabs}\t/* D * sqrt(2)       */ .scale({D * math.sqrt(2):.2f})\n"
       f"{tabs}\t.build();\n")
    circuit = lambda tabs: (
       f"{tabs}auto sk = SecKey(ctx);\n"
       f"{tabs}sk.GenSecKey();\n"
       f"{tabs}addSome1DMatrices(sk);\n"
       f"{tabs}PubKey& pk = sk;\n\n"
       f"{tabs}auto pt = Ptxt<BGV>(ctx);\n"
       f"{tabs}for (size_t i = 0; i < {slots}; ++i) {{\n"
       f"{tabs}\tpt[i] = msg[i];\n"
       f"{tabs}}}\n"
       f"{tabs}auto ct = Ctxt(pk);\n"
       f"{tabs}pk.Encrypt(ct, pt);\n\n"
       f"{tabs}for (size_t i = 0; i < {muls}; ++i) {{\n"
       f"{tabs}\tauto tmp = ct;\n"
       f"{tabs}\ttmp.multiplyBy(ct);\n"
       f"{tabs}\ttmp *= {factor}l;\n"
       f"{tabs}\tfor (size_t j = 1; j < {sums}; ++j) {{\n"
       f"{tabs}\t\ttmp += ct;\n"
       f"{tabs}\t}}\n"
       f"{tabs}\tfor (size_t j = 0; j < {rots}; ++j) {{\n"
       f"{tabs}\t\tint by = (i & 1) ^ (j & 1);\n"
       f"{tabs}\t\trotate(tmp, by);\n"
       f"{tabs}\t}}\n"
       f"{tabs}\tct = tmp;\n"
       f"{tabs}}}\n\n"
       f"{tabs}auto dec = Ptxt<BGV>(ctx);\n"
       f"{tabs}sk.Decrypt(dec, ct);\n")

    msg  = mainmsg(t, slots)
    cmp  = (
        "\tstd::cout << \"dec: ( \";\n"
       f"\tfor (size_t i = 0; i < {min(10, slots)}; ++i) {{\n"
        "\t\tstd::cout << (int64_t)dec[i] << \" \";\n"
        "\t}\n"
        "\tstd::cout << \")\" << std::endl;\n\n"
        "\tstd::cout << \"cmp: ( \";\n"
       f"{maincmp(t, muls, const, rots, sums, slots, False, min(10, slots))}"
        "\tstd::cout << \")\" << std::endl;\n")
    ctx1 = ctx("\t")

    main = ctx1 + msg + circuit("\t") + cmp
    writemain(config.HELIB_INC, config.HELIB_USE, main)

    msg = benchmsg(d, t)
    bench_ctx = benchloop(ctx("\t\t"), 'ctx')
    bench_gen = ctx1 + "\n" + benchloop((
        "\t\tauto sk = SecKey(ctx);\n"
        "\t\tsk.GenSecKey();\n"
        "\t\taddSome1DMatrices(sk);\n"
        "\t\tPubKey& pk = sk;\n\n"), 'pk')
    bench_enc = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
    ) + benchloop((
        "\t\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\t\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\t\tpt[i] = msg[i];\n"
        "\t\t}\n"
        "\t\tauto ct = Ctxt(pk);\n"
        "\t\tpk.Encrypt(ct, pt);\n"), 'ct')
    bench_dec = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
        "\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\tpt[i] = msg[i];\n"
        "\t}\n"
        "\tauto ct = Ctxt(pk);\n"
        "\tpk.Encrypt(ct, pt);\n\n"
    ) + benchloop((
        "\t\tauto dec = Ptxt<BGV>(ctx);\n"
        "\t\tsk.Decrypt(dec, ct);\n"), 'dec')
    bench_mul = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
        "\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\tpt[i] = msg[i];\n"
        "\t}\n"
        "\tauto ct = Ctxt(pk);\n"
        "\tpk.Encrypt(ct, pt);\n\n"
    ) + benchloop((
        "\t\tauto prod = ct;\n"
        "\t\tprod.multiplyBy(ct);\n"), 'prod')
    bench_const = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
        "\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\tpt[i] = msg[i];\n"
        "\t}\n"
        "\tauto ct = Ctxt(pk);\n"
        "\tpk.Encrypt(ct, pt);\n\n"
        "\tint64_t factor = dist(rng);\n"
    ) + benchloop((
        "\t\tauto prod = ct;\n"
        "\t\tprod *= factor;\n"), 'prod')
    bench_rot = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
        "\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\tpt[i] = msg[i];\n"
        "\t}\n"
        "\tauto ct = Ctxt(pk);\n"
        "\tpk.Encrypt(ct, pt);\n\n"
        "\tint64_t by = dist(rng);\n"
    ) + benchloop((
        "\t\tauto rot = ct;\n"
        "\t\trotate(rot, by);\n"), 'rot')
    bench_add = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto sk = SecKey(ctx);\n"
        "\tsk.GenSecKey();\n"
        "\taddSome1DMatrices(sk);\n"
        "\tPubKey& pk = sk;\n\n"
        "\tauto pt = Ptxt<BGV>(ctx);\n"
       f"\tfor (size_t i = 0; i < {slots}; ++i) {{\n"
        "\t\tpt[i] = msg[i];\n"
        "\t}\n"
        "\tauto ct = Ctxt(pk);\n"
        "\tpk.Encrypt(ct, pt);\n\n"
    ) + benchloop((
        "\t\tauto sum = ct;\n"
        "\t\tsum += ct;\n"), 'sum')
    bench_all = ctx1 + "\n" + msg + "\n" + benchloop(circuit("\t\t"), 'dec')

    bench = bench_ctx, bench_gen, bench_enc, bench_dec, bench_mul, bench_const, bench_rot, bench_add, bench_all
    writebench(config.HELIB_INC, config.HELIB_USE, bench)


def writepalisade(m, t, logq0, logql, ops, keyswitch, omega=4, secret='Ternary', sigma=3.2):
    writemake(config.PALISADE_INCS, config.PALISADE_LIBS)

    muls, const, rots, sums = ops
    if const > 0:
        raise ValueError("const > 0")

    d       = util.phi(m)
    slots   = util.slots(m, t)
    primes  = muls + 1
    encrypt = 'ctx->ModReduce(ctx->Encrypt(keys.publicKey, pt));'

    if keyswitch == 'GHS':
        w = 1

    if secret == 'Ternary':
        sdist = 'OPTIMIZED'
    elif secret == 'Error':
        sdist = 'RLWE'
    else:
        raise ValueError("secret not in ['Ternary', 'Error']")

    ctx = lambda tabs: (
       f"{tabs}auto ctx = CryptoContextFactory<DCRTPoly>::genCryptoContextBGVrns(\n"
       f"{tabs}\t/* L - 1              */ {primes},\n"
       f"{tabs}\t/* plaintext modulus  */ {t},\n"
       f"{tabs}\t/* security level     */ HEStd_NotSet,\n"
       f"{tabs}\t/* standard deviation */ {sigma},\n"
       f"{tabs}\t/* maximum depth      */ 2,\n"
       f"{tabs}\t/* key distribution   */ {sdist},\n"
       f"{tabs}\t/* keyswitch method   */ {keyswitch.upper()},\n"
       f"{tabs}\t/* ring dimension     */ {d},\n"
       f"{tabs}\t/* omega HYBRID       */ {omega},\n"
       f"{tabs}\t/* log2(p0)           */ {logq0},\n"
       f"{tabs}\t/* log2(pl)           */ {logql},\n"
       f"{tabs}\t/* omega BV           */ {omega},\n"
       f"{tabs}\t/* batch size         */ {slots},\n"
       f"{tabs}\t/* modswitch method   */ MANUAL);\n"
       f"{tabs}ctx->Enable(ENCRYPTION);\n"
       f"{tabs}ctx->Enable(SHE);\n"
       f"{tabs}ctx->Enable(LEVELEDSHE);\n")
    circuit = lambda tabs: (
       f"{tabs}auto keys = ctx->KeyGen();\n"
       f"{tabs}auto pt   = ctx->MakePackedPlaintext(msg);\n"
       f"{tabs}auto ct   = {encrypt}\n"
       f"{tabs}ctx->EvalMultKeyGen(keys.secretKey);\n"
       f"{tabs}ctx->EvalAtIndexKeyGen(keys.secretKey, {{1, -1}});\n\n"
       f"{tabs}for (size_t i = 0; i < {muls}; ++i) {{\n"
       f"{tabs}\tauto tmp = ctx->EvalMult(ct, ct);\n"
       f"{tabs}\tfor (size_t j = 1; j < {sums}; ++j) {{\n"
       f"{tabs}\t\ttmp = ctx->EvalAdd(tmp, ct);\n"
       f"{tabs}\t}}\n"
       f"{tabs}\tfor (size_t j = 0; j < {rots}; ++j) {{\n"
       f"{tabs}\t\tint by = (i & 1) ^ (j & 1);\n"
       f"{tabs}\t\ttmp = ctx->EvalAtIndex(tmp, by);\n"
       f"{tabs}\t}}\n"
       f"{tabs}\tct = ctx->ModReduce(tmp);\n"
       f"{tabs}}}\n\n"
       f"{tabs}Plaintext dec;\n"
       f"{tabs}ctx->Decrypt(keys.secretKey, ct, &dec);\n")

    msg  = mainmsg(t, slots)
    cmp  = (
       f"\tdec->SetLength({min(10, slots)});\n"
        "\tstd::cout << \"dec: \" << dec << std::endl;\n\n"
        "\tstd::cout << \"cmp: ( \";\n"
       f"{maincmp(t, muls, const, rots, sums, slots, True, min(10, slots))}"
        "\tstd::cout << \"... )\" << std::endl;\n")
    ctx1 = ctx("\t")

    main = ctx1 + msg + circuit("\t") + cmp
    writemain(config.PALISADE_INC, config.PALISADE_USE, main)

    msg = benchmsg(d, t)
    bench_ctx = benchloop(ctx("\t\t"), 'ctx')
    bench_gen = ctx1 + "\n" + benchloop((
        "\t\tauto keys = ctx->KeyGen();\n"
        "\t\tctx->EvalMultKeyGen(keys.secretKey);\n"
        "\t\tctx->EvalAtIndexKeyGen(keys.secretKey, {1, -1});\n"), 'keys')
    bench_enc = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto keys = ctx->KeyGen();\n"
    ) + benchloop((
        "\t\tauto pt = ctx->MakePackedPlaintext(msg);\n"
       f"\t\tauto ct = {encrypt};\n"), 'ct')
    bench_dec = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto keys = ctx->KeyGen();\n"
        "\tauto pt = ctx->MakePackedPlaintext(msg);\n"
       f"\tauto ct = {encrypt};\n"
    ) + benchloop((
        "\t\tPlaintext dec;\n"
        "\t\tctx->Decrypt(keys.secretKey, ct, &dec);\n"), 'dec')
    bench_mul = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto keys = ctx->KeyGen();\n"
        "\tauto pt = ctx->MakePackedPlaintext(msg);\n"
       f"\tauto ct = {encrypt};\n"
        "\tctx->EvalMultKeyGen(keys.secretKey);\n"
    ) + benchloop("\t\tauto prod = ctx->EvalMult(ct, ct);\n", 'prod')
    bench_rot = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tint by = dist(rng);\n"
        "\tauto keys = ctx->KeyGen();\n"
        "\tctx->EvalAtIndexKeyGen(keys.secretKey, {by});\n"
        "\tauto pt = ctx->MakePackedPlaintext(msg);\n"
       f"\tauto ct = {encrypt};\n"
    ) + benchloop("\t\tauto rot = ctx->EvalAtIndex(ct, by);\n", 'rot')
    bench_add = (
       f"{ctx1}\n"
       f"{msg}\n"
        "\tauto keys = ctx->KeyGen();\n"
        "\tauto pt = ctx->MakePackedPlaintext(msg);\n"
       f"\tauto ct = {encrypt};\n"
    ) + benchloop("\t\tauto sum = ctx->EvalAdd(ct, ct);\n", 'sum')
    bench_all = ctx1 + "\n" + msg + "\n" + benchloop(circuit("\t\t"), 'dec')

    bench = bench_ctx, bench_gen, bench_enc, bench_dec, bench_mul, None, bench_rot, bench_add, bench_all
    writebench(config.PALISADE_INC, config.PALISADE_USE, bench)
