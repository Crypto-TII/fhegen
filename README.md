# FheGEN: Parameters Generation for FHE Schemes

[![BGV Parameters](https://img.shields.io/badge/BGV%20Parameters-Download-green)](https://eprint.iacr.org/2022/706.pdf)
[![BFV Parameters](https://img.shields.io/badge/BFV%20Parameters-Download-red)](https://eprint.iacr.org/2023/600.pdf)
[![Slack](https://img.shields.io/badge/slack-@fhegen-yellow.svg?logo=slack)](https://join.slack.com/t/fhegen/shared_invite/zt-2rtezhwty-i9h4Vmcc~Oiw0bSwgHxTMw)
[![Docker Guide](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=orange)](Dockerfile)

---

## Introduction 🎉

FheGEN is a tool for generating cryptographic parameters for leveled Fully Homomorphic Encryption (FHE) schemes, specifically BGV and BFV. Developed through a collaboration between the **Crypto Research Center at the Technology Innovation Institute** and the **Chair of Security Engineering at Ruhr University Bochum**, FheGEN helps researchers and practitioners efficiently determine secure and optimized FHE parameters.

## Getting Started 🚀

FheGEN can be run interactively from the terminal to generate customized encryption parameters.

### Prerequisites ✔️

- **[SageMath](https://doc.sagemath.org/html/en/installation/index.html)** and **[Python 3](https://www.python.org/downloads/)** must be installed.

### Running FheGEN ✈️

1. Clone the repository:

    ```md
    git clone https://github.com/Crypto-TII/fhegen.git
    cd fhegen
    ```
2. Execute the interactive script:

    ```md
    sage -python3 src/interactive.py
    ```
   
## Docker Support 🐳

FheGEN includes a pre-configured **Dockerfile** for seamless deployment. Users can build and run the containerized environment as needed.
> 💡 **Note:** You must have [Docker installed](https://docs.docker.com/get-docker/) on your system to use this feature.

### Build the Docker Image

To create the Docker image, navigate to the project root directory and execute:

```md
docker build -t fhegen .
```

### Launch an Interactive Container


To run the Docker container interactively, use the following command:

```md 
docker run -it --name fhegen-dev --entrypoint /bin/bash fhegen
```

Once inside the container, manually run:

```md
sage -python3 src/interactive.py
```

**Note:** Feel free to customize the Docker setup to suit your workflow such as adding volumes (via docker-compose), changing entrypoints, or applying other preferences.

## Usage

FheGEN will prompt you to configure key parameters, including `circuit model`, `multiplicative depth`, `key-switching method`, and `library selection`.

### Example Output

Let `R = Z [x]/(x^n+1)`, where `n` is a power of `2`.
We denote the plaintext modulus by `t` and the ciphertext modulus by `q`, which are typically chosen such that `t << q`.

```md
Generated your BFV configuration!
model: Base
sec:   116
n:     4096
t:     65537
logq:  84
logP:  35
```

In the case of BGV, the ciphertext modulus `q` is a product of primes:
`q =p_0 * ... * p_{L-1}`. The multiplicative depth `M` determines the number of moduli, with `L = M + 1`.

```md
Generated your BGV configuration!  
model: Base                 # Chosen circuit model (e.g., Base)
sec:   137                  # Estimated security level
n:     4096                 # Polynomial degree
t:     65537                # Plaintext modulus
logq:  65 (31, 30, 4)       # Ciphertext modulus size, split into bottom, middle, and top moduli
logP:  36                   # Key-switching modulus size
```

#### Moduli Breakdown for the BGV scheme

A homomorphic encryption circuit uses `multiple levels` to control noise growth via `modulus switching`.  The ciphertext modulus `q` is a product of primes `p_i` (with `i in [0, L-1]`) split into three types: top, middle, and bottom modulus as follows:

| Modulus Type     | Description                                                                        |
| ---------------- |------------------------------------------------------------------------------------|
| `Top Modulus`    | The top modulus is the first modulus in the prime chain. It is applied immediately after encryption to reduce the initial noise to a smaller value `B`. |
| `Middle Moduli`  | After the arithmetic operations defined by the circuit model (see below), we reduce the noise back to `B` using the modulus switching procedure.|
| `Bottom Modulus` | The bottom modulus is the last modulus in the prime chain. No key switching or modulus switching is applied after the final multiplication; decryption is done directly using the extended secret key. This ensures correctness without further noise reduction.  |

#### Circuit Models

FheGEN supports different circuit models (as in Fig.1 of [[1](https://eprint.iacr.org/2022/706.pdf)]).
The selected circuits perform a sequence of operations on `η` ciphertexts `c_i` in parallel. The resulting ciphertext is then homomorphically multiplied with another one, computed in the same way. This process is repeated M times.

| Model Type      | Description                                                                                                                                            |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Base Model`    | Performs a constant multiplication on each ciphertext, then sums the results before the homomorphic multiplication                                     |
| `Model 1`       | Extends the Base Model performing `τ` rotations *after* the constant multiplications                                                                   |
| `Model 2`       | Extends the Base Model performing `τ` rotations *before* the constant multiplications                                                                  |
| `OpenFHE Model` | Inspired by OpenFHE,  each ciphertext `c_i` is the result of a homomorphic multiplication. These `η` ciphertexts are then summed and rotated `τ` times |

### Library Selection

The generated code is a setup routine for the chosen library and provides references to further code examples within the respective library.

> #### ⚠️ Limitations
> Some parameter sets may not be supported by all libraries due to internal constraints. For example, OpenFHE only supports plaintext moduli up to 60 bits.
Choosing a larger modulus will result in code that may not compile or execute correctly.


## Security

To enable faster and more flexible parameter selection, we empirically fine-tune a formula that links the security level `λ` to the dimension `n`, given the ciphertext modulus size (`log q`) and the secret distribution. The formula is based on the best-known attacks on lattice problems and provides a quick security estimate for parameter generation.

A detailed security analysis of the formula is provided in  [[1](https://eprint.iacr.org/2022/706.pdf)].

## Get Help

For questions or bug reports, please open an [issue](https://github.com/Crypto-TII/fhegen/issues) or contact us at `chiara.marcolla (at) tii.ae` or `johannes.mono (at) rub.de`.

## Cite 📖

```
@misc{cryptoeprint:2022/706,
      author = {Johannes Mono and Chiara Marcolla and Georg Land and Tim Güneysu and Najwa Aaraj},
      title = {Finding and Evaluating Parameters for {BGV}},
      howpublished = {Cryptology ePrint Archive, Paper 2022/706},
      year = {2022},
      note = {\url{https://eprint.iacr.org/2022/706}},
      url = {https://eprint.iacr.org/2022/706}
}

@misc{cryptoeprint:2023/600,
      author = {Beatrice Biasioli and Chiara Marcolla and Marco Calderini and Johannes Mono},
      title = {Improving and Automating {BFV} Parameters Selection: An Average-Case Approach},
      howpublished = {Cryptology {ePrint} Archive, Paper 2023/600},
      year = {2023},
      url = {https://eprint.iacr.org/2023/600}
}
```
