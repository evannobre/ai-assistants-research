#!/usr/bin/env python3
"""
FASTA simulation using naïve Linear Congruential Generator
Implements the sequential algorithm as specified.
"""

import sys


class NaiveLCG:
    """Naïve Linear Congruential Generator implementation"""
    
    def __init__(self, seed=42):
        self.IM = 139968
        self.IA = 3877
        self.IC = 29573
        self.seed = seed
    
    def random(self, max_val):
        """Generate random number using LCG formula"""
        self.seed = (self.seed * self.IA + self.IC) % self.IM
        return max_val * self.seed / self.IM


def convert_to_cumulative_probabilities(probabilities):
    """Convert expected probabilities to cumulative probabilities"""
    cumulative = []
    running_sum = 0.0
    
    for prob in probabilities:
        running_sum += prob[1]  # prob[1] is the probability value
        cumulative.append((prob[0], running_sum))  # prob[0] is the nucleotide
    
    return cumulative


def select_nucleotide_linear_search(cumulative_probs, random_val):
    """Select nucleotide using linear search against cumulative probabilities"""
    for nucleotide, cum_prob in cumulative_probs:
        if random_val <= cum_prob:
            return nucleotide
    # Fallback to last nucleotide if floating point errors occur
    return cumulative_probs[-1][0]


def generate_repeat_sequence(sequence, length, line_width=60):
    """Generate DNA sequence by copying from a given sequence"""
    result = []
    seq_len = len(sequence)
    
    for i in range(length):
        if i > 0 and i % line_width == 0:
            result.append('\n')
        result.append(sequence[i % seq_len])
    
    return ''.join(result)


def generate_random_sequence(probabilities, length, lcg, line_width=60):
    """Generate DNA sequence by weighted random selection"""
    # Convert to cumulative probabilities
    cumulative_probs = convert_to_cumulative_probabilities(probabilities)
    
    result = []
    
    for i in range(length):
        if i > 0 and i % line_width == 0:
            result.append('\n')
        
        # Generate random number using LCG
        random_val = lcg.random(1.0)
        
        # Select nucleotide using linear search
        nucleotide = select_nucleotide_linear_search(cumulative_probs, random_val)
        result.append(nucleotide)
    
    return ''.join(result)


def main():
    # Parse command line argument
    if len(sys.argv) != 2:
        print("Usage: python fasta.py <length>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: Length must be an integer")
        sys.exit(1)
    
    # Initialize LCG with seed 42
    lcg = NaiveLCG(42)
    
    # ALU sequence for repeat generation
    alu_sequence = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    
    # IUB probabilities for random generation
    iub_probabilities = [
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
        ('Y', 0.02)
    ]
    
    # Homosapiens probabilities for random generation
    homosapiens_probabilities = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    
    # Generate and output sequences
    
    # 1. Generate repeat sequence (ALU)
    print(">ONE Homo sapiens alu")
    repeat_seq = generate_repeat_sequence(alu_sequence, n * 2)
    print(repeat_seq)
    if not repeat_seq.endswith('\n'):
        print()
    
    # 2. Generate random sequence (IUB)
    print(">TWO IUB ambiguity codes")
    iub_seq = generate_random_sequence(iub_probabilities, n * 3, lcg)
    print(iub_seq)
    if not iub_seq.endswith('\n'):
        print()
    
    # 3. Generate random sequence (Homo sapiens)
    print(">THREE Homo sapiens frequency")
    homo_seq = generate_random_sequence(homosapiens_probabilities, n * 5, lcg)
    print(homo_seq)
    if not homo_seq.endswith('\n'):
        print()


if __name__ == "__main__":
    main()