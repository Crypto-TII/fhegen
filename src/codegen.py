import config
import util


def openfhe(params):
    if params['scheme'] == 'BGV':
        ctx = ((
            f"\tCCParams<CryptoContextBGVRNS> params;\n"
            f"\tparams.SetMultiplicativeDepth({params['depth']});\n"
            f"\tparams.SetPlaintextModulus({params['t']});\n"
            f"\tparams.SetSecurityLevel(HEStd_NotSet);\n"
            f"\tparams.SetSecretKeyDist({params['sdist']});\n"
            f"\tparams.SetRingDim({params['d']});\n"
            f"\tparams.SetFirstModSize({params['q0bits']});\n"
            f"\tparams.SetScalingModSize({params['qlbits']});\n"
            f"\tparams.SetBatchSize({params['slots']});\n"
            f"\tparams.SetScalingTechnique(FLEXIBLEAUTOEXT);\n\n"
            f"\t// see {config.OPENFHE_LINK_BGV} for a full OpenFHE BGV example\n"
            f"\t// ...\n\n"))
    elif params['scheme'] == 'BFV':
        ctx = ((
            f"\tCCParams<CryptoContextBFVRNS> params;\n"
            f"\tparams.SetMultiplicativeDepth({params['depth']});\n"
            f"\tparams.SetPlaintextModulus({params['t']});\n"
            f"\tparams.SetSecurityLevel(HEStd_NotSet);\n"
            f"\tparams.SetSecretKeyDist({params['sdist']});\n"
            f"\tparams.SetRingDim({params['d']});\n"
            f"\tparams.SetFirstModSize({params['q0bits']});\n"
            f"\tparams.SetScalingModSize({params['qlbits']});\n"
            f"\tparams.SetBatchSize({params['slots']});\n\n"
            f"\t// see {config.OPENFHE_LINK_BFV} for a full OpenFHE BFV example\n"
            f"\t// ...\n\n"))

    with open("openfhe.cpp", "w+") as f:
        f.write("#include \"openfhe.h\"\nusing namespace lbcrypto;\n\nint main(void)\n{\n" + ctx + "\treturn 0;\n}\n")


def palisade(params):
    if params['scheme'] == 'BGV':
        ctx = ((
            f"\tauto ctx = CryptoContextFactory<DCRTPoly>::genCryptoContextBGVrns(\n"
            f"\t\t/* L - 1              */ {params['depth']},\n"
            f"\t\t/* plaintext modulus  */ {params['t']},\n"
            f"\t\t/* security level     */ HEStd_NotSet,\n"
            f"\t\t/* standard deviation */ {params['sigma']},\n"
            f"\t\t/* maximum depth      */ 2,\n"
            f"\t\t/* key distribution   */ {params['sdist']},\n"
            f"\t\t/* ring dimension     */ {params['d']},\n"
            f"\t\t/* log2(p0)           */ {params['q0bits']},\n"
            f"\t\t/* log2(pl)           */ {params['qlbits']},\n"
            f"\t\t/* batch size         */ {params['slots']},\n"
            f"\t\t/* modswitch method   */ AUTO);\n\n"
            f"\t// see {config.PALISADE_LINK_BGV} for a full PALISADE BGV example\n"
            f"\t// ...\n\n"))
    elif params['scheme'] == 'BFV':
        ctx = ((
            f"\tauto ctx = CryptoContextFactory<DCRTPoly>::genCryptoContextBFVrns(\n"
            f"\t\t/* plaintext modulus  */ {params['t']},\n"
            f"\t\t/* security level     */ HEStd_NotSet,\n"
            f"\t\t/* standard deviation */ {params['sigma']},\n"
            f"\t\t/* ciphertext sums    */ {params['sums']},\n"
            f"\t\t/* L - 1              */ {params['depth']},\n"
            f"\t\t/* rotation count     */ {params['rots']},\n"
            f"\t\t/* key distribution   */ {params['sdist']},\n"
            f"\t\t/* maximum depth      */ 2,\n"
            f"\t\t/* log2(pi)           */ {params['qlbits']},\n"
            f"\t\t/* ring dimension     */ {params['d']});\n\n"
            f"\t// see {config.PALISADE_LINK_BFV} for a full PALISADE BFV example\n"
            f"\t// ...\n\n"))

    with open("palisade.cpp", "w+") as f:
        f.write("#include \"palisade.h\"\nusing namespace lbcrypto;\n\nint main(void)\n{\n" + ctx + "\treturn 0;\n}\n")


def seal(params):
    mods = []
    for m in params['q']:
        mods.append(f"Modulus({m})")
    mvec = f"{{{', '.join(mods)}}}"

    if params['scheme'] == 'BGV':
        ctx = ((
            f"\tEncryptionParameters params(scheme_type::bgv);\n"
            f"\tparams.set_poly_modulus_degree({params['d']});\n"
            f"\tparams.set_coeff_modulus({mvec});\n"
            f"\tparams.set_plain_modulus({params['t']});\n\n"
            f"\t// see {config.SEAL_LINK_BGV} for a full SEAL BGV example\n"
            f"\t// ...\n\n"))
    elif params['scheme'] == 'BFV':
        ctx = ((
            f"\tEncryptionParameters params(scheme_type::bfv);\n"
            f"\tparams.set_poly_modulus_degree({params['d']});\n"
            f"\tparams.set_coeff_modulus({mvec});\n"
            f"\tparams.set_plain_modulus({params['t']});\n\n"
            f"\t// see {config.SEAL_LINK_BGV} for a full SEAL BFV example\n"
            f"\t// ...\n\n"))

    with open("seal.cpp", "w+") as f:
        f.write("#include \"seal/seal.h\"\nusing namespace seal;\n\nint main(void)\n{\n" + ctx + "\treturn 0;\n}\n")
