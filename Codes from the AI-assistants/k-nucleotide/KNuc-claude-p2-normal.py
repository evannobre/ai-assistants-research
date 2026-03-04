#!/usr/bin/env python3
"""
K-Nucleotide DNA Sequence Analysis
Efficient implementation using native Python libraries (Counter from collections)
Optimized for memory and performance on systems with 8GB RAM
"""

import sys
from collections import Counter
from typing import Iterator


def read_dna_sequence(filename: str) -> str:
    """
    Read DNA sequence from FASTA file, extracting sequence after '>THREE' marker.
    Memory-efficient: reads line by line instead of loading entire file.
    
    Args:
        filename: Path to FASTA format DNA file
        
    Returns:
        Complete DNA sequence as uppercase string
    """
    sequence_parts = []
    in_target_sequence = False
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Check for sequence header
                if line.startswith('>'):
                    if 'THREE' in line:
                        in_target_sequence = True
                    else:
                        in_target_sequence = False
                    continue
                
                # Collect sequence data
                if in_target_sequence:
                    sequence_parts.append(line.upper())
        
        return ''.join(sequence_parts)
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def generate_kmers(sequence: str, k: int) -> Iterator[str]:
    """
    Generator that yields all k-mers from a DNA sequence.
    Memory-efficient: yields one k-mer at a time instead of creating a list.
    
    Args:
        sequence: DNA sequence string
        k: Length of k-mer
        
    Yields:
        k-mer substrings of length k
    """
    seq_len = len(sequence)
    for i in range(seq_len - k + 1):
        yield sequence[i:i + k]


def calculate_frequencies(sequence: str, k: int) -> Counter:
    """
    Calculate k-mer frequencies using Counter (native hash table implementation).
    
    Args:
        sequence: DNA sequence string
        k: Length of k-mer
        
    Returns:
        Counter object with k-mer frequencies
    """
    return Counter(generate_kmers(sequence, k))


def print_frequency_table(sequence: str, k: int) -> None:
    """
    Print frequency table for k-mers of length k, sorted by frequency (descending)
    then alphabetically.
    
    Args:
        sequence: DNA sequence string
        k: Length of k-mer
    """
    freq_counter = calculate_frequencies(sequence, k)
    total = sum(freq_counter.values())
    
    # Sort by frequency (descending), then by k-mer (ascending)
    sorted_items = sorted(
        freq_counter.items(),
        key=lambda x: (-x[1], x[0])
    )
    
    for kmer, count in sorted_items:
        percentage = (count * 100.0) / total
        print(f"{kmer} {percentage:.3f}")
    print()


def print_kmer_count(sequence: str, kmer: str) -> None:
    """
    Print the count of a specific k-mer in the sequence.
    
    Args:
        sequence: DNA sequence string
        kmer: Specific k-mer to count
    """
    k = len(kmer)
    freq_counter = calculate_frequencies(sequence, k)
    count = freq_counter[kmer.upper()]
    print(f"{count}\t{kmer}")


def main():
    """
    Main execution function for k-nucleotide analysis.
    Follows the benchmark specification for output format.
    """
    if len(sys.argv) != 2:
        print("Usage: python k_nucleotide.py <dna_fasta_file>", file=sys.stderr)
        print("\nExample: python k_nucleotide.py input.fasta", file=sys.stderr)
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read DNA sequence
    sequence = read_dna_sequence(filename)
    
    if not sequence:
        print("Error: No DNA sequence found in file.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Sequence length: {len(sequence)} nucleotides\n")
    
    # Generate frequency tables for k=1 and k=2
    print_frequency_table(sequence, 1)
    print_frequency_table(sequence, 2)
    
    # Count specific k-mers
    specific_kmers = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    
    for kmer in specific_kmers:
        print_kmer_count(sequence, kmer)


if __name__ == '__main__':
    main()
