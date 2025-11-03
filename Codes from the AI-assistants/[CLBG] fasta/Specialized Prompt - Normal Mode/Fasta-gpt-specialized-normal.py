#!/usr/bin/env python3

import sys

# Linear Congruential Generator parameters
IM = 139968
IA = 3877
IC = 29573
seed = 42

def random(maxval):
    global seed
    seed = (seed * IA + IC) % IM
    return maxval * seed / IM

def make_cumulative(frequencies):
    cumulative = []
    total = 0.0
    for ch, prob in frequencies:
        total += prob
        cumulative.append((ch, total))
    return cumulative

def select_random_nucleotide(cumulative):
    r = random(1.0)
    for ch, cum_prob in cumulative:
        if r < cum_prob:
            return ch
    return cumulative[-1][0]  # Fallback, should rarely hit due to float precision

def repeat_sequence(seq, n):
    """Emit a repeated sequence up to length n"""
    seq = seq.replace('\n', '')
    length = len(seq)
    i = 0
    while n > 0:
        line_len = min(60, n)
        end = i + line_len
        print(seq[i % length:end % length] if end % length > i % length else (seq[i % length:] + seq[:end % length]))
        i = (i + line_len) % length
        n -= line_len

def random_sequence(cumulative, n):
    """Emit a sequence of random bases based on cumulative probabilities"""
    line = []
    while n > 0:
        line.clear()
        for _ in range(min(60, n)):
            line.append(select_random_nucleotide(cumulative))
        print(''.join(line))
        n -= 60

def main():
    try:
        n = int(sys.argv[1])
    except (IndexError, ValueError):
        n = 25000000

    # First DNA sequence (copied)
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    iub = [
        ('a', 0.27),
        ('c', 0.12),
        ('g', 0.12),
        ('t', 0.27),
        ('B', 0.02),
        ('D', 0.02),
        ('H', 0.02),
        ('K', 0.02),
        ('M', 0.02),
        ('N', 0.02),
        ('R', 0.02),
        ('S', 0.02),
        ('V', 0.02),
        ('W', 0.02),
        ('Y', 0.02),
    ]

    homosapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008),
    ]

    iub_cumulative = make_cumulative(iub)
    homo_cumulative = make_cumulative(homosapiens)

    # Emit headers and DNA
    print(">ONE Homo sapiens alu")
    repeat_sequence(alu, n)

    print(">TWO IUB ambiguity codes")
    random_sequence(iub_cumulative, n)

    print(">THREE Homo sapiens frequency")
    random_sequence(homo_cumulative, n)

if __name__ == "__main__":
    main()
