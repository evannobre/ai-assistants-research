#!/usr/bin/env python3
"""
FASTA simulation using naïve Linear Congruential Generator
"""

import sys

# LCG constants
IM = 139968
IA = 3877
IC = 29573
seed = 42

# Sequences
ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

# IUB codes
IUB = [
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

# Homosapiens codes
HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


def random(max_val):
    """Naïve Linear Congruential Generator"""
    global seed
    seed = (seed * IA + IC) % IM
    return max_val * seed / IM


def make_cumulative(genelist):
    """Convert probabilities to cumulative probabilities"""
    cumulative = []
    cp = 0.0
    for char, prob in genelist:
        cp += prob
        cumulative.append((char, cp))
    return cumulative


def select_random(cumulative):
    """Select a nucleotide using linear search against cumulative probabilities"""
    r = random(1.0)
    for char, cp in cumulative:
        if r < cp:
            return char
    return cumulative[-1][0]


def make_repeat_fasta(id, desc, src, n):
    """Generate DNA by copying from a given sequence"""
    print(f">{id} {desc}")
    src_len = len(src)
    pos = 0
    line_length = 60
    
    while n > 0:
        if n < line_length:
            line_length = n
        
        line = ""
        for _ in range(line_length):
            line += src[pos]
            pos = (pos + 1) % src_len
        
        print(line)
        n -= line_length


def make_random_fasta(id, desc, genelist, n):
    """Generate DNA by weighted random selection"""
    print(f">{id} {desc}")
    cumulative = make_cumulative(genelist)
    line_length = 60
    
    while n > 0:
        if n < line_length:
            line_length = n
        
        line = ""
        for _ in range(line_length):
            line += select_random(cumulative)
        
        print(line)
        n -= line_length


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    make_repeat_fasta("ONE", "Homo sapiens alu", ALU, n * 2)
    make_random_fasta("TWO", "IUB ambiguity codes", IUB, n * 3)
    make_random_fasta("THREE", "Homo sapiens frequency", HOMOSAPIENS, n * 5)


if __name__ == "__main__":
    main()
