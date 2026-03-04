#!/usr/bin/env python3
import sys
from itertools import cycle, islice

# LCG constants (naive)
IM = 139968
IA = 3877
IC = 29573
_seed = 42  # module-level seed (mutable via function)

def random_max(max_value):
    """Naive LCG: update global seed and return float in [0, max_value)."""
    global _seed
    _seed = (_seed * IA + IC) % IM
    return (max_value * _seed) / IM

def cumulative(probs):
    """Convert list of probabilities to cumulative probabilities (float)."""
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)
    return cum

def pick_from_cumulative(alphabet, cum_probs):
    """Generate one symbol by calling the naive LCG and linear-searching cum_probs."""
    r = random_max(1.0)
    # linear search
    for i, c in enumerate(cum_probs):
        if r < c:
            return alphabet[i]
    return alphabet[-1]  # fallback (shouldn't happen if cum_probs[-1] == 1.0)

def repeat_sequence(source, n):
    """Produce n characters by repeating source; yield lines of 60 chars."""
    # Use cycle to repeat source, then chunk into 60-char lines
    it = islice(cycle(source), n)
    buf = []
    count = 0
    for ch in it:
        buf.append(ch)
        count += 1
        if count == 60:
            yield ''.join(buf)
            buf = []
            count = 0
    if buf:
        yield ''.join(buf)

def random_sequence_from_alphabet(alphabet, probs, n):
    """Produce n characters by weighted random selection using naive LCG."""
    cum = cumulative(probs)
    buf = []
    count = 0
    for _ in range(n):
        buf.append(pick_from_cumulative(alphabet, cum))
        count += 1
        if count == 60:
            yield ''.join(buf)
            buf = []
            count = 0
    if buf:
        yield ''.join(buf)

def main():
    # default length if not provided
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except:
            n = 25000000
    else:
        n = 25000000

    # Example source sequence (ALU fragment commonly used in FASTA benchmark)
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    # First block: copy from alu, length n
    # Print header like FASTA
    sys.stdout.write(">ONE Homo sapiens alu\n")
    for line in repeat_sequence(alu, n):
        sys.stdout.write(line + "\n")

    # Second block: weighted random from IUB ambiguity codes (example)
    sys.stdout.write(">TWO IUB ambiguity codes\n")
    iub_alphabet = list("acgtBDHKMNRSVWY")  # example extended alphabet
    iub_probs = [
        0.27, 0.12, 0.12, 0.27,  # a,c,g,t
        0.02, 0.02, 0.02, 0.02,  # B,D,H,K
        0.02, 0.02, 0.02, 0.02,  # M,N,R,S
        0.02, 0.02               # V,W,Y
    ]
    # Normalize to sum 1.0 (defensive)
    s = sum(iub_probs)
    iub_probs = [p / s for p in iub_probs]

    for line in random_sequence_from_alphabet(iub_alphabet, iub_probs, n):
        sys.stdout.write(line + "\n")

    # Third block: Homo sapiens nucleotide frequencies (example)
    sys.stdout.write(">THREE Homo sapiens frequency\n")
    homo_alphabet = list("acgt")
    homo_probs = [0.3029549426680, 0.1979883004921,
                  0.1975473066391, 0.3015094502008]
    # Normalize (should already sum to 1)
    s = sum(homo_probs)
    homo_probs = [p / s for p in homo_probs]

    for line in random_sequence_from_alphabet(homo_alphabet, homo_probs, n):
        sys.stdout.write(line + "\n")

if __name__ == "__main__":
    main()
