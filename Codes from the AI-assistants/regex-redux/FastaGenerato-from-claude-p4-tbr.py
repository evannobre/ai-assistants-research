#!/usr/bin/env python3
"""
FASTA Format Generator
Generates pseudo-random DNA sequences in FASTA format for testing.
Based on the standard fasta benchmark generator.
"""

import sys


# IUB ambiguity codes with their probabilities
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

# Homosapiens DNA sequence frequencies
HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]

# Linear Congruential Generator constants
IM = 139968
IA = 3877
IC = 29573
LAST = 42

LINE_LENGTH = 60


def makeCumulative(table):
    """Convert probability table to cumulative probabilities."""
    cumulative = []
    cp = 0.0
    for char, prob in table:
        cp += prob
        cumulative.append((char, cp))
    return cumulative


def selectRandom(cumulative_table):
    """Select a random character based on cumulative probabilities."""
    global LAST
    LAST = (LAST * IA + IC) % IM
    r = LAST / IM
    
    for char, prob in cumulative_table:
        if r < prob:
            return char
    return cumulative_table[-1][0]


def makeRandomFasta(desc, table, n):
    """Generate random FASTA sequence."""
    cumulative = makeCumulative(table)
    print(f'>{desc}')
    
    line = []
    for i in range(n):
        line.append(selectRandom(cumulative))
        if len(line) == LINE_LENGTH:
            print(''.join(line))
            line = []
    
    if line:
        print(''.join(line))


def makeRepeatFasta(desc, sequence, n):
    """Generate repeating FASTA sequence."""
    print(f'>{desc}')
    
    seq_len = len(sequence)
    extended = sequence * ((n // seq_len) + 1)
    
    for i in range(0, n, LINE_LENGTH):
        end = min(i + LINE_LENGTH, n)
        print(extended[i:end])


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <length>', file=sys.stderr)
        print(f'Example: {sys.argv[0]} 5000000 > input5000000.txt', file=sys.stderr)
        sys.exit(1)
    
    n = int(sys.argv[1])
    
    # ALU sequence (a common repeating element in human DNA)
    alu = (
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
    )
    
    makeRepeatFasta('ONE Homo sapiens alu', alu, n * 2)
    makeRandomFasta('TWO IUB ambiguity codes', IUB, n * 3)
    makeRandomFasta('THREE Homo sapiens frequency', HOMOSAPIENS, n * 5)


if __name__ == '__main__':
    main()
