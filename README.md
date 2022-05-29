# fhegen
This is a parameter generator for the leveled BGV scheme, joint work by
the Crypto Research Center at the Technology Innovation Institute and
the Chair of Security Engineering at Ruhr University Bochum.

## Usage
Interactive Mode: `python src/bgv.py`

Feel free to browse the source code or open an issue if you encounter
any problems with the generator.

## Output
```
Generated your BGV configuration!
sec:   147.55
d:     16384
t:     65537
logq:  405 (32, 33, 4)
logP:  11
slots: 16384
Generating Makefile, main.cpp and bench.cpp for PALISADE.
```

The output provides multiple values: the estimated security `sec`,
the polynomial degree `d`, the plaintext modulus `t` and the size of the
ciphertext modulus `logq` including the sizes for the top and bottom modulus
as well as the middle moduli (see below). In addition, we output the size of
the key switching modulus `logP` and the amount of plaintext slots available.

The top modulus is the first modulus in the prime chain, that is the modulus
to be switched down from directly after encryption, and the bottom modulus is
the modulus that is left before decrypting. The middle moduli are the other
moduli in the middle.

Note that due to some discrepancies with HElib and PALISADE internals,
some parameter sets might not work. If you encounter such a parameter set,
or any other format, please open an issue or send us an email to
`johannes.mono (at) rub.de`.

## Cite
Coming soon on ePrint...
