#!/usr/bin/env python3
"""
FASTA sequence generation using naive Linear Congruential Generator.
Implements the benchmark specifications without optimizations.
"""

import sys


# Linear Congruential Generator constants
IM = 139968
IA = 3877
IC = 29573
seed = 42


def random_lcg(max_val):
    """
    Naive LCG implementation - generates random number in range [0, max_val).
    Updates global seed as per specification.
    """
    global seed
    seed = (seed * IA + IC) % IM
    return (max_val * seed) / IM


# Amino acid alphabet with probabilities
ALU = "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"


# IUB nucleotide probabilities
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


# Homosapiens nucleotide probabilities
HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


def make_cumulative(alphabet):
    """
    Convert probabilities to cumulative probabilities.
    Returns list of (nucleotide, cumulative_probability) tuples.
    """
    cumulative = []
    cumulative_prob = 0.0
    
    for nucleotide, probability in alphabet:
        cumulative_prob += probability
        cumulative.append((nucleotide, cumulative_prob))
    
    return cumulative


def select_random(cumulative_alphabet):
    """
    Select a nucleotide using weighted random selection with linear search.
    Matches random number against cumulative probabilities.
    """
    random_val = random_lcg(1.0)
    
    # Linear search through cumulative probabilities
    for nucleotide, cumulative_prob in cumulative_alphabet:
        if random_val < cumulative_prob:
            return nucleotide
    
    # Fallback (should not reach here with proper probabilities)
    return cumulative_alphabet[-1][0]


def make_repeat_fasta(header, sequence, n):
    """
    Generate DNA sequence by repeating a given sequence.
    """
    print(f">{header}")
    
    seq_len = len(sequence)
    pos = 0
    line_length = 60
    
    while n > 0:
        if n < line_length:
            line_length = n
        
        # Handle wrapping around the sequence
        if pos + line_length <= seq_len:
            print(sequence[pos:pos + line_length])
            pos += line_length
        else:
            # Need to wrap around
            part1 = sequence[pos:]
            remaining = line_length - len(part1)
            part2 = sequence[:remaining]
            print(part1 + part2)
            pos = remaining
        
        n -= line_length


def make_random_fasta(header, alphabet, n):
    """
    Generate DNA sequence by weighted random selection from alphabet.
    Uses cumulative probabilities and linear search.
    """
    print(f">{header}")
    
    # Convert to cumulative probabilities
    cumulative = make_cumulative(alphabet)
    
    line_length = 60
    line = []
    
    for i in range(n):
        # Select nucleotide using LCG and cumulative probability lookup
        nucleotide = select_random(cumulative)
        line.append(nucleotide)
        
        # Print line when we reach line_length or end of sequence
        if len(line) == line_length or i == n - 1:
            print(''.join(line))
            line = []


def main():
    """
    Main entry point for FASTA sequence generation.
    """
    if len(sys.argv) < 2:
        print("Usage: python fasta.py <n>", file=sys.stderr)
        print("Example: python fasta.py 25000000", file=sys.stderr)
        sys.exit(1)
    
    n = int(sys.argv[1])
    
    # Generate sequences as per specification
    make_repeat_fasta("ONE Homo sapiens alu", ALU, n * 2)
    make_random_fasta("TWO IUB ambiguity codes", IUB, n * 3)
    make_random_fasta("THREE Homo sapiens frequency", HOMOSAPIENS, n * 5)


if __name__ == "__main__":
    main()
