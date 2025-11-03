#!/usr/bin/env python3
"""
K-Nucleotide Simulation Algorithm
Optimized implementation using Python's built-in dictionary (hash table)
for counting k-nucleotide sequences in DNA data.
"""

import sys
from collections import defaultdict
from typing import Dict, List, Tuple


def read_fasta_sequence_three(file_handle) -> str:
    """
    Read FASTA format file and extract DNA sequence THREE.
    Returns the concatenated DNA sequence as uppercase string.
    """
    sequence_lines = []
    sequence_found = False
    
    for line in file_handle:
        line = line.strip()
        if line.startswith('>'):
            if 'THREE' in line.upper():
                sequence_found = True
            elif sequence_found:
                # Found next sequence header, stop reading
                break
        elif sequence_found and line:
            # Add sequence data
            sequence_lines.append(line.upper())
    
    return ''.join(sequence_lines)


def update_nucleotide_counts(sequence: str, k: int, counts: Dict[str, int]) -> None:
    """
    Update hash table of k-nucleotide keys and count values for a particular k-length.
    This function processes all reading frames and updates the provided hash table.
    
    Args:
        sequence: DNA sequence string
        k: Length of nucleotide subsequences to count
        counts: Hash table (dictionary) to store k-nucleotide counts
    """
    seq_length = len(sequence)
    
    # Process all possible k-nucleotide subsequences
    for i in range(seq_length - k + 1):
        kmer = sequence[i:i + k]
        # Update count in hash table - lookup and increment
        if kmer in counts:
            counts[kmer] += 1
        else:
            counts[kmer] = 1


def calculate_frequencies(counts: Dict[str, int]) -> List[Tuple[float, str]]:
    """
    Calculate percentage frequencies and sort by descending frequency, 
    then ascending k-nucleotide key.
    """
    total_count = sum(counts.values())
    
    # Create list of (frequency, nucleotide) tuples
    freq_list = []
    for nucleotide, count in counts.items():
        frequency = (count * 100.0) / total_count
        freq_list.append((frequency, nucleotide))
    
    # Sort by descending frequency, then ascending nucleotide key
    freq_list.sort(key=lambda x: (-x[0], x[1]))
    
    return freq_list


def format_frequency_output(freq_list: List[Tuple[float, str]]) -> None:
    """Format and print frequency results."""
    for frequency, nucleotide in freq_list:
        print(f"{nucleotide} {frequency:.3f}")


def count_specific_sequences(sequence: str, target_sequences: List[str]) -> Dict[str, int]:
    """
    Count occurrences of specific nucleotide sequences.
    Returns dictionary with sequence counts.
    """
    results = {}
    
    for target in target_sequences:
        k = len(target)
        count = 0
        seq_length = len(sequence)
        
        # Count all occurrences of target sequence
        for i in range(seq_length - k + 1):
            if sequence[i:i + k] == target:
                count += 1
        
        results[target] = count
    
    return results


def main():
    """Main execution function."""
    try:
        # Read DNA sequence THREE from stdin
        dna_sequence = read_fasta_sequence_three(sys.stdin)
        
        if not dna_sequence:
            print("Error: Could not find DNA sequence THREE in input", file=sys.stderr)
            sys.exit(1)
        
        print(f"Processing DNA sequence of length: {len(dna_sequence)}")
        
        # Process 1-nucleotide sequences
        print("\n1-nucleotide frequencies:")
        counts_1 = {}
        update_nucleotide_counts(dna_sequence, 1, counts_1)
        freq_1 = calculate_frequencies(counts_1)
        format_frequency_output(freq_1)
        
        # Process 2-nucleotide sequences  
        print("\n2-nucleotide frequencies:")
        counts_2 = {}
        update_nucleotide_counts(dna_sequence, 2, counts_2)
        freq_2 = calculate_frequencies(counts_2)
        format_frequency_output(freq_2)
        
        # Count specific sequences
        target_sequences = [
            "GGT",           # 3-nucleotide
            "GGTA",          # 4-nucleotide  
            "GGTATT",        # 6-nucleotide
            "GGTATTTTAATT",  # 12-nucleotide
            "GGTATTTTAATTTATAGT"  # 18-nucleotide
        ]
        
        print("\nSpecific sequence counts:")
        specific_counts = count_specific_sequences(dna_sequence, target_sequences)
        
        for sequence in target_sequences:
            count = specific_counts[sequence]
            print(f"{count}\t{sequence}")
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()