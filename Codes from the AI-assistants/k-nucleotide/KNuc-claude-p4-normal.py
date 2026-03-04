#!/usr/bin/env python3
"""
K-Nucleotide Counting Algorithm
Implements the k-nucleotide benchmark using native Python data structures.
"""

import sys
from collections import defaultdict
from typing import Dict


def read_fasta_sequence(stream) -> str:
    """
    Read FASTA format from stdin and extract DNA sequence THREE.
    
    Args:
        stream: Input stream (typically sys.stdin)
    
    Returns:
        DNA sequence as uppercase string
    """
    lines = []
    reading_three = False
    
    for line in stream:
        line = line.rstrip()
        
        if line.startswith('>'):
            # Check if this is sequence THREE
            if '>THREE' in line:
                reading_three = True
            else:
                # If we were reading THREE and hit another header, we're done
                if reading_three:
                    break
                reading_three = False
        elif reading_three:
            lines.append(line.upper())
    
    return ''.join(lines)


def update_frequency_table(sequence: str, k: int, freq_table: Dict[str, int]) -> None:
    """
    Update hash table with k-nucleotide counts for all reading frames.
    
    This function counts k-mers by sliding a window of size k across
    the entire sequence, updating the frequency table for each k-mer found.
    
    Args:
        sequence: DNA sequence string
        k: Length of k-nucleotide to count
        freq_table: Hash table (dict) to update with counts
    """
    seq_len = len(sequence)
    
    # Slide window across all reading frames
    for i in range(seq_len - k + 1):
        kmer = sequence[i:i + k]
        # Lookup current count and update
        freq_table[kmer] = freq_table.get(kmer, 0) + 1


def calculate_frequencies(sequence: str, k: int) -> Dict[str, int]:
    """
    Calculate k-nucleotide frequencies for a given k.
    
    Args:
        sequence: DNA sequence
        k: Length of nucleotide sequence
    
    Returns:
        Dictionary with k-nucleotide frequencies
    """
    freq_table = {}
    update_frequency_table(sequence, k, freq_table)
    return freq_table


def write_frequencies(sequence: str, k: int) -> None:
    """
    Write k-nucleotide frequencies sorted by descending frequency,
    then ascending k-nucleotide key.
    
    Args:
        sequence: DNA sequence
        k: Length of nucleotide sequence
    """
    freq_table = calculate_frequencies(sequence, k)
    total = sum(freq_table.values())
    
    # Sort by frequency (descending), then by key (ascending)
    sorted_items = sorted(
        freq_table.items(),
        key=lambda x: (-x[1], x[0])
    )
    
    for kmer, count in sorted_items:
        percentage = (count * 100.0) / total
        print(f"{kmer} {percentage:.3f}")
    
    print()


def write_count(sequence: str, target: str) -> None:
    """
    Write the count for a specific nucleotide sequence.
    
    Args:
        sequence: DNA sequence
        target: Target nucleotide sequence to count
    """
    k = len(target)
    freq_table = calculate_frequencies(sequence, k)
    count = freq_table.get(target.upper(), 0)
    print(f"{count}\t{target}")


def main():
    """
    Main execution function.
    Reads FASTA input and performs all required k-nucleotide counts.
    """
    # Read DNA sequence THREE from stdin
    sequence = read_fasta_sequence(sys.stdin)
    
    # Task 1: Count and write 1-nucleotide frequencies
    write_frequencies(sequence, 1)
    
    # Task 2: Count and write 2-nucleotide frequencies
    write_frequencies(sequence, 2)
    
    # Task 3: Count specific sequences
    write_count(sequence, "GGT")
    write_count(sequence, "GGTA")
    write_count(sequence, "GGTATT")
    write_count(sequence, "GGTATTTTAATT")
    write_count(sequence, "GGTATTTTAATTTATAGT")


if __name__ == "__main__":
    main()
