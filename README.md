# fhegen
This is a parameter generator for the leveled BGV and BFV scheme, joint
work by the Crypto Research Center at the Technology Innovation Institute
and the Chair of Security Engineering at Ruhr University Bochum.

## Usage
Interactive Mode: `python src/interactive.py`

Feel free to browse the source code or open an issue if you encounter
any problems with the generator.

## Output
```
Generated your BGV configuration!
model: Base
sec:   137
d:     4096
t:     65537
qbits: 65 (31, 30, 4)
Pbits: 36
```

The output provides multiple values: the chosen model 'model', the estimated
security `sec`, the polynomial degree `d`, the plaintext modulus `t` and the
size of the ciphertext modulus `qbits` including the sizes for the top and
bottom modulus as well as the middle moduli (see below). In addition, we output
the size of the key switching modulus `Pbits`.

The top modulus is the first modulus in the prime chain, that is the modulus
to be switched down from directly after encryption, and the bottom modulus is
the modulus that is left before decrypting. The middle moduli are the other
moduli in the middle.

Note that due to some discrepancies with library internals, some parameter sets
might not work as expected. If you encounter such a parameter set or have any
other questions, open an issue or send an email to `johannes.mono (at) rub.de`.

## Cite
The accompanying paper is available on ePrint. For citations, please use
the snippet below.

```
@misc{cryptoeprint:2022/706,
      author = {Johannes Mono and Chiara Marcolla and Georg Land and Tim Güneysu and Najwa Aaraj},
      title = {Finding and Evaluating Parameters for {BGV}},
      howpublished = {Cryptology ePrint Archive, Paper 2022/706},
      year = {2022},
      note = {\url{https://eprint.iacr.org/2022/706}},
      url = {https://eprint.iacr.org/2022/706}
}
```
