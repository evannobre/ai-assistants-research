#!/usr/bin/env python3
"""
K-Nucleotide DNA Sequence Analyzer
Counts frequency of nucleotide sequences of varying lengths in DNA data.
Uses Python's native dict for optimal performance.
"""

import sys
from collections import defaultdict


def read_sequence(filename):
    """Read DNA sequence from FASTA file, extracting sequence after '>THREE'."""
    with open(filename, 'r') as f:
        # Skip to the line starting with '>THREE'
        for line in f:
            if line.startswith('>THREE'):
                break
        
        # Read and concatenate all sequence lines, converting to uppercase
        sequence = []
        for line in f:
            if line.startswith('>'):
                break
            sequence.append(line.strip().upper())
        
        return ''.join(sequence)


def count_kmers(sequence, k):
    """Count all k-mers in the sequence using native dict."""
    counts = defaultdict(int)
    seq_len = len(sequence)
    
    # Slide window of size k through sequence
    for i in range(seq_len - k + 1):
        kmer = sequence[i:i + k]
        counts[kmer] += 1
    
    return dict(counts)


def print_frequencies(counts, sequence_length, k):
    """Print k-mer frequencies sorted by count (descending) then alphabetically."""
    total = sequence_length - k + 1
    
    # Sort by count (descending), then by sequence (ascending)
    sorted_kmers = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    for kmer, count in sorted_kmers:
        percentage = (count * 100.0) / total
        print(f"{kmer} {percentage:.3f}")
    print()


def print_count(counts, sequence):
    """Print count for a specific sequence."""
    count = counts.get(sequence, 0)
    print(f"{count}\t{sequence}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python k_nucleotide.py <fasta_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read the DNA sequence
    sequence = read_sequence(filename)
    seq_len = len(sequence)
    
    print(f"Sequence length: {seq_len}\n")
    
    # Generate and print k=1 frequencies
    counts_1 = count_kmers(sequence, 1)
    print_frequencies(counts_1, seq_len, 1)
    
    # Generate and print k=2 frequencies
    counts_2 = count_kmers(sequence, 2)
    print_frequencies(counts_2, seq_len, 2)
    
    # Count specific sequences
    specific_sequences = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    
    for seq in specific_sequences:
        k = len(seq)
        counts = count_kmers(sequence, k)
        print_count(counts, seq)


if __name__ == "__main__":
    main()
