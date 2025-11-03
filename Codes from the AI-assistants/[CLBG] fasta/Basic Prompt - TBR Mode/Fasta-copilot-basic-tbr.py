#!/usr/bin/env python3
import sys
from bisect import bisect   # native binary‐search for the cumulative array

# LCG constants (naïve, unoptimized)
IM = 139968
IA = 3877
IC = 29573
_seed = 42

def rand_float():
    """
    Update the global seed using the LCG, then
    return a float in [0,1).
    """
    global _seed
    _seed = (IA * _seed + IC) % IM
    return _seed / IM

def make_cumprobs(weights):
    """
    Given an ordered list of (char, weight),
    return two lists: [chars], [cumulative sums normalized to 1).
    """
    chars, w = zip(*weights)
    total = float(sum(w))
    cum = []
    s = 0.0
    for wi in w:
        s += wi
        cum.append(s / total)
    return list(chars), cum

def emit_wrapped(data, width=60):
    """
    Take a sequence string, write it to stdout
    in lines of at most `width` chars.
    """
    for i in range(0, len(data), width):
        sys.stdout.write(data[i : i + width] + "\n")

def repeat_fasta(header, seq, length):
    """
    Print a repeated copy of `seq` up to `length`.
    """
    sys.stdout.write(f">{header}\n")
    full_repeats = length // len(seq)
    remainder = length % len(seq)
    # Build one big chunk so we can wrap it
    out = seq * full_repeats + seq[:remainder]
    emit_wrapped(out)

def random_fasta(header, chars, cumprobs, length):
    """
    Print `length` bases by weighted sampling from `chars`.
    Uses rand_float() and bisect on `cumprobs`.
    """
    sys.stdout.write(f">{header}\n")
    # build into a list of characters, then join & wrap
    out = []
    for _ in range(length):
        r = rand_float()
        # find first index where cumprobs[i] > r
        idx = bisect(cumprobs, r)
        out.append(chars[idx])
    emit_wrapped("".join(out))

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <n>", file=sys.stderr)
        sys.exit(1)

    n = int(sys.argv[1])

    # IUB ambiguity codes
    iub = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]

    # Homo sapiens frequency (from the benchmark spec)
    homo = [
        ('a', 0.3029549426680), ('c', 0.1979883004921),
        ('g', 0.1975473066391), ('t', 0.3015094502008)
    ]

    # Make cumulative distributions
    chars_iub,  cum_iub  = make_cumprobs(iub)
    chars_homo, cum_homo = make_cumprobs(homo)

    # The “given” sequence for the first block
    alu_seq = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    # produce outputs
    repeat_fasta("ONE Homo sapiens alu", alu_seq, n)
    random_fasta("TWO IUB ambiguity codes", chars_iub, cum_iub, n)
    random_fasta("THREE Homo sapiens frequency",    chars_homo, cum_homo, n)

if __name__ == "__main__":
    main()
