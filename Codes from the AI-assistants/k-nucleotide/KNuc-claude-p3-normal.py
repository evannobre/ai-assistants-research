#!/usr/bin/env python3
"""
K-nucleotide counting algorithm
Reads FASTA format, extracts sequence THREE, counts k-nucleotide frequencies
"""

import sys
from collections import defaultdict


def read_fasta_sequence(name):
    """Read FASTA format from stdin and extract the specified sequence"""
    line = sys.stdin.readline()
    while line:
        if line.startswith('>'):
            if name in line:
                # Found the target sequence, read all subsequent lines until next header
                sequence = []
                line = sys.stdin.readline()
                while line and not line.startswith('>'):
                    sequence.append(line.rstrip())
                    line = sys.stdin.readline()
                return ''.join(sequence).upper()
        line = sys.stdin.readline()
    return ''


def update_frequencies(sequence, length, frequencies):
    """
    Update hash table with k-nucleotide counts for a particular reading frame.
    This function grows the hash table from default size as needed.
    
    Args:
        sequence: DNA sequence string
        length: k-nucleotide length
        frequencies: hash table (dict) to update
    """
    seq_len = len(sequence)
    # Process all reading frames by sliding window
    for i in range(seq_len - length + 1):
        key = sequence[i:i + length]
        # Lookup current count and update
        frequencies[key] = frequencies.get(key, 0) + 1


def calculate_frequencies(sequence, length):
    """
    Count all k-nucleotide sequences of given length.
    Creates hash table and calls update function.
    
    Args:
        sequence: DNA sequence string
        length: k-nucleotide length
    
    Returns:
        Dictionary with k-nucleotide counts
    """
    frequencies = {}  # Start with small default size, will grow
    update_frequencies(sequence, length, frequencies)
    return frequencies


def write_frequencies(sequence, length):
    """
    Count and write k-nucleotide frequencies sorted by descending frequency,
    then ascending k-nucleotide key
    """
    frequencies = calculate_frequencies(sequence, length)
    total = sum(frequencies.values())
    
    # Sort by descending frequency, then ascending key
    sorted_items = sorted(frequencies.items(), 
                         key=lambda x: (-x[1], x[0]))
    
    for key, count in sorted_items:
        percentage = (count * 100.0) / total
        print(f'{key} {percentage:.3f}')
    print()


def write_count(sequence, target):
    """
    Count and write the count for a specific k-nucleotide sequence
    """
    length = len(target)
    frequencies = calculate_frequencies(sequence, length)
    count = frequencies.get(target, 0)
    print(f'{count}\t{target}')


def main():
    # Read sequence THREE from FASTA input
    sequence = read_fasta_sequence('THREE')
    
    if not sequence:
        print("Error: Could not find sequence THREE", file=sys.stderr)
        return
    
    # Count 1-nucleotide and 2-nucleotide sequences
    # Write with descending frequency, ascending key sort
    write_frequencies(sequence, 1)
    write_frequencies(sequence, 2)
    
    # Count specific sequences
    targets = [
        'GGT',
        'GGTA',
        'GGTATT',
        'GGTATTTTAATT',
        'GGTATTTTAATTTATAGT'
    ]
    
    for target in targets:
        write_count(sequence, target)


if __name__ == '__main__':
    main()
