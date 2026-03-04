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

def random(max_val):
    """Generate random number using naïve LCG"""
    global seed
    seed = (seed * IA + IC) % IM
    return max_val * seed / IM

# Sequences and probabilities
ALU = (
    'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
    'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
    'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
    'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
    'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
    'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
    'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
)

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

HOMO_SAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]

def make_cumulative(table):
    """Convert probabilities to cumulative probabilities"""
    cumulative = []
    cum_prob = 0.0
    for char, prob in table:
        cum_prob += prob
        cumulative.append((char, cum_prob))
    return cumulative

def select_random(cumulative):
    """Select a character using linear search through cumulative probabilities"""
    r = random(1.0)
    for char, cum_prob in cumulative:
        if r < cum_prob:
            return char
    return cumulative[-1][0]

def make_repeat_fasta(header, seq, n):
    """Generate DNA by repeating a sequence"""
    print(f'>{header}')
    seq_len = len(seq)
    pos = 0
    line_length = 60
    
    while n > 0:
        if n < line_length:
            line_length = n
        
        line = ''
        for _ in range(line_length):
            line += seq[pos]
            pos = (pos + 1) % seq_len
        
        print(line)
        n -= line_length

def make_random_fasta(header, table, n):
    """Generate DNA by weighted random selection"""
    print(f'>{header}')
    cumulative = make_cumulative(table)
    line_length = 60
    
    while n > 0:
        if n < line_length:
            line_length = n
        
        line = ''
        for _ in range(line_length):
            line += select_random(cumulative)
        
        print(line)
        n -= line_length

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    make_repeat_fasta('ONE Homo sapiens alu', ALU, n * 2)
    make_random_fasta('TWO IUB ambiguity codes', IUB, n * 3)
    make_random_fasta('THREE Homo sapiens frequency', HOMO_SAPIENS, n * 5)

if __name__ == '__main__':
    main()
