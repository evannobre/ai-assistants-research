#!/usr/bin/env python3
"""
K-Nucleotide DNA Sequence Analyzer
Efficiently counts and analyzes nucleotide sequences of varying lengths.
Optimized for memory and performance on systems with limited resources.
"""

import sys
from collections import Counter
from typing import Iterator, Dict
import argparse


def read_sequence(filepath: str, header: str = '>THREE') -> str:
    """
    Read DNA sequence from FASTA file after specified header.
    Memory-efficient streaming approach for large files.
    
    Args:
        filepath: Path to the FASTA file
        header: Header line to start reading from
        
    Returns:
        Concatenated uppercase DNA sequence
    """
    sequence_parts = []
    reading = False
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if line.startswith(header):
                        reading = True
                    elif reading:
                        # Stop if we hit another header after starting
                        break
                elif reading:
                    sequence_parts.append(line.upper())
        
        return ''.join(sequence_parts)
    
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def generate_kmers(sequence: str, k: int) -> Iterator[str]:
    """
    Generate all k-mers from a sequence using a sliding window.
    Generator approach to minimize memory usage.
    
    Args:
        sequence: DNA sequence string
        k: Length of k-mer
        
    Yields:
        k-mer substrings
    """
    seq_len = len(sequence)
    for i in range(seq_len - k + 1):
        yield sequence[i:i + k]


def count_kmers(sequence: str, k: int) -> Counter:
    """
    Count all k-mers in the sequence using native Counter.
    
    Args:
        sequence: DNA sequence string
        k: Length of k-mer
        
    Returns:
        Counter object with k-mer frequencies
    """
    return Counter(generate_kmers(sequence, k))


def calculate_frequencies(counts: Counter, total: int) -> Dict[str, float]:
    """
    Calculate frequency percentages for k-mers.
    
    Args:
        counts: Counter with k-mer counts
        total: Total number of k-mers
        
    Returns:
        Dictionary mapping k-mers to their frequency percentages
    """
    return {kmer: (count / total) * 100 for kmer, count in counts.items()}


def print_frequency_table(counts: Counter, k: int) -> None:
    """
    Print sorted frequency table for k-mers.
    
    Args:
        counts: Counter with k-mer counts
        k: Length of k-mer
    """
    total = sum(counts.values())
    frequencies = calculate_frequencies(counts, total)
    
    # Sort by frequency (descending), then alphabetically
    sorted_kmers = sorted(frequencies.items(), 
                         key=lambda x: (-x[1], x[0]))
    
    for kmer, freq in sorted_kmers:
        print(f"{kmer} {freq:.3f}")


def print_sequence_count(counts: Counter, sequence: str) -> None:
    """
    Print count for a specific sequence.
    
    Args:
        counts: Counter with k-mer counts
        sequence: Specific sequence to lookup
    """
    count = counts.get(sequence.upper(), 0)
    print(f"{count}\t{sequence.upper()}")


def analyze_sequence(filepath: str) -> None:
    """
    Main analysis function following the k-nucleotide benchmark specification.
    
    Args:
        filepath: Path to FASTA file
    """
    # Read the DNA sequence
    sequence = read_sequence(filepath)
    
    if not sequence:
        print("Error: No sequence data found.", file=sys.stderr)
        sys.exit(1)
    
    # Calculate k-mer frequencies for k=1 and k=2
    print("# k=1 frequencies:")
    counts_1 = count_kmers(sequence, 1)
    print_frequency_table(counts_1, 1)
    print()
    
    print("# k=2 frequencies:")
    counts_2 = count_kmers(sequence, 2)
    print_frequency_table(counts_2, 2)
    print()
    
    # Count specific sequences
    specific_sequences = [
        ('GGT', 3),
        ('GGTA', 4),
        ('GGTATT', 6),
        ('GGTATTTTAATT', 12),
        ('GGTATTTTAATTTATAGT', 18)
    ]
    
    print("# Specific sequence counts:")
    for seq, k in specific_sequences:
        counts = count_kmers(sequence, k)
        print_sequence_count(counts, seq)


def main():
    """Entry point for the k-nucleotide analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze k-nucleotide frequencies in DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s input.fasta
  %(prog)s /path/to/dna_sequence.txt
        """
    )
    parser.add_argument(
        'filepath',
        help='Path to FASTA format DNA sequence file'
    )
    
    args = parser.parse_args()
    
    analyze_sequence(args.filepath)


if __name__ == '__main__':
    main()
