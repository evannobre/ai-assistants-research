#!/usr/bin/env python3
import sys
from itertools import accumulate, cycle, islice

class LCG:
    """
    Simple 32-bit LCG:
      Xₙ₊₁ = (1664525·Xₙ + 1013904223) mod 2^32
    """
    def __init__(self, seed=42):
        self.state = seed & 0xFFFFFFFF

    def next_int(self):
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def rand(self):
        # float in [0,1)
        return self.next_int() / 2**32


def make_cdf(alphabet, weights):
    """Return list of (cum_prob, letter). weights need not sum to 1."""
    total = float(sum(weights))
    cum = list(accumulate(w/total for w in weights))
    return list(zip(cum, alphabet))


def rand_sequence(gen, cdf, length):
    """Yield `length` random letters using CDF and RNG.gen."""
    for _ in range(length):
        r = gen.rand()
        # linear scan through CDF; for small alphabets this is fine
        for cum_prob, letter in cdf:
            if r < cum_prob:
                yield letter
                break


def wrap_and_print(name, seq_iter, total_len, width=60, out=sys.stdout):
    """Emit a FASTA block named `>name`, wrapping seq_iter at `width`."""
    print(f">{name}", file=out)
    taken = islice(seq_iter, total_len)
    while True:
        chunk = "".join(islice(taken, width))
        if not chunk:
            break
        print(chunk, file=out)


if __name__ == "__main__":
    # parameters from the classic “fasta” benchmark
    SEED = 42
    lcg = LCG(SEED)

    # 1) output a repeating sequence (“>ONE”)
    alu = ("A","L","U","A","R","I","A","L","U")  # example pattern
    wrap_and_print("ONE", cycle(alu), total_len=2**20, width=60)

    # 2) random with IUB ambiguity codes
    iub_letters  = list("GATCRYMWSKBDHVN")
    iub_weights  = [0.27,0.12,0.12,0.27,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02]
    cdf_iub      = make_cdf(iub_letters, iub_weights)
    wrap_and_print("RANDOM_IUB", rand_sequence(lcg, cdf_iub, 3*2**18), total_len=3*2**18)

    # 3) random with Homo sapiens frequency
    hs_letters = list("ACGT")
    hs_weights = [0.3029549426680,
                  0.1979883004921,
                  0.1975473066391,
                  0.3015094502008]
    cdf_hs     = make_cdf(hs_letters, hs_weights)
    wrap_and_print("RANDOM_HS", rand_sequence(lcg, cdf_hs, 3*2**18), total_len=3*2**18)
