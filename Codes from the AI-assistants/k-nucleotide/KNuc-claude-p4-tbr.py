#!/usr/bin/env python3
"""
K-Nucleotide DNA Sequence Counter
Implements the k-nucleotide benchmark following best practices
"""

import sys
from collections import defaultdict


def read_fasta_sequence(stream):
    """
    Read FASTA format and extract DNA sequence THREE.
    
    Args:
        stream: Input stream (e.g., sys.stdin)
    
    Returns:
        str: DNA sequence in uppercase
    """
    lines = []
    found_three = False
    
    for line in stream:
        line = line.rstrip()
        
        if line.startswith('>'):
            if found_three:
                break
            if 'THREE' in line.upper():
                found_three = True
        elif found_three:
            lines.append(line.upper())
    
    return ''.join(lines)


def update_frequencies(sequence, length, frequencies):
    """
    Update hash table with k-nucleotide frequencies for given length.
    
    This function processes all reading frames and updates the frequency
    count for each k-nucleotide substring of the specified length.
    
    Args:
        sequence: DNA sequence string
        length: k-nucleotide length
        frequencies: defaultdict to update with counts
    """
    seq_len = len(sequence)
    
    # Process all reading frames (sliding window)
    for i in range(seq_len - length + 1):
        nucleotide = sequence[i:i + length]
        frequencies[nucleotide] += 1


def calculate_frequencies(sequence, length):
    """
    Calculate k-nucleotide frequencies and return sorted results.
    
    Args:
        sequence: DNA sequence string
        length: k-nucleotide length
    
    Returns:
        list: Sorted list of (nucleotide, percentage) tuples
    """
    frequencies = defaultdict(int)
    update_frequencies(sequence, length, frequencies)
    
    total = sum(frequencies.values())
    
    # Sort by descending frequency, then ascending key
    result = []
    for nucleotide, count in frequencies.items():
        percentage = (count * 100.0) / total
        result.append((nucleotide, percentage))
    
    result.sort(key=lambda x: (-x[1], x[0]))
    return result


def count_sequence(sequence, target):
    """
    Count occurrences of a specific nucleotide sequence.
    
    Args:
        sequence: DNA sequence string
        target: Target nucleotide sequence to count
    
    Returns:
        int: Count of occurrences
    """
    length = len(target)
    frequencies = defaultdict(int)
    update_frequencies(sequence, length, frequencies)
    return frequencies[target]


def format_frequency_output(results):
    """
    Format frequency results for output.
    
    Args:
        results: List of (nucleotide, percentage) tuples
    
    Returns:
        str: Formatted output string
    """
    output = []
    for nucleotide, percentage in results:
        output.append(f"{nucleotide} {percentage:.3f}")
    return '\n'.join(output)


def main():
    """Main execution function."""
    # Read DNA sequence THREE from stdin
    sequence = read_fasta_sequence(sys.stdin)
    
    # 1-nucleotide frequencies
    freq_1 = calculate_frequencies(sequence, 1)
    print(format_frequency_output(freq_1))
    print()
    
    # 2-nucleotide frequencies
    freq_2 = calculate_frequencies(sequence, 2)
    print(format_frequency_output(freq_2))
    print()
    
    # Specific sequence counts
    targets = [
        'GGT',
        'GGTA',
        'GGTATT',
        'GGTATTTTAATT',
        'GGTATTTTAATTTATAGT'
    ]
    
    for target in targets:
        count = count_sequence(sequence, target)
        print(f"{count}\t{target}")


if __name__ == '__main__':
    main()
