#!/usr/bin/env python3
"""
K-Nucleotide frequency counter for DNA sequences.
Uses native Python data structures (dict and Counter).
"""

import sys
from collections import Counter, defaultdict


def read_sequence(filename):
    """Read DNA sequence from FASTA file, filtering for sequence THREE."""
    with open(filename, 'r') as f:
        in_target = False
        sequence = []
        
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if 'THREE' in line:
                    in_target = True
                else:
                    in_target = False
            elif in_target:
                sequence.append(line.upper())
        
        return ''.join(sequence)


def count_kmers(sequence, k):
    """Count all k-mers in sequence using native Counter."""
    kmers = [sequence[i:i+k] for i in range(len(sequence) - k + 1)]
    return Counter(kmers)


def print_frequency_table(counts, total):
    """Print k-mer frequencies sorted by count (descending), then alphabetically."""
    items = [(kmer, count) for kmer, count in counts.items()]
    items.sort(key=lambda x: (-x[1], x[0]))
    
    for kmer, count in items:
        percentage = (count * 100.0) / total
        print(f"{kmer} {percentage:.3f}")
    print()


def print_specific_count(counts, target):
    """Print count for a specific k-mer."""
    count = counts.get(target.upper(), 0)
    print(f"{count}\t{target}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <fasta_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read the DNA sequence
    sequence = read_sequence(filename)
    
    if not sequence:
        print("Error: No sequence found or sequence THREE not found")
        sys.exit(1)
    
    print(f"Sequence length: {len(sequence)}\n")
    
    # Count k-mers of different lengths
    counts_1 = count_kmers(sequence, 1)
    counts_2 = count_kmers(sequence, 2)
    
    # Print frequency tables for k=1 and k=2
    total_1 = len(sequence)
    print_frequency_table(counts_1, total_1)
    
    total_2 = len(sequence) - 1
    print_frequency_table(counts_2, total_2)
    
    # Count and print specific sequences
    for length, target in [(3, 'GGT'), (4, 'GGTA'), (6, 'GGTATT'),
                           (12, 'GGTATTTTAATT'), (18, 'GGTATTTTAATTTATAGT')]:
        counts = count_kmers(sequence, length)
        print_specific_count(counts, target)


if __name__ == '__main__':
    main()
