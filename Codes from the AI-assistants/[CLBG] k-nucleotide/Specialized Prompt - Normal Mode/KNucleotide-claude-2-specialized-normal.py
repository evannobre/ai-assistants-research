#!/usr/bin/env python3
"""
Optimized K-Nucleotide Simulation Algorithm
Uses DNA letter to byte mapping (A=0, C=1, G=2, T=3) for improved performance
while maintaining the same algorithmic approach.
"""

import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


# DNA letter to byte mapping
DNA_TO_BYTE = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
BYTE_TO_DNA = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}


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
            # Add sequence data, filtering invalid characters
            clean_line = ''.join(c for c in line.upper() if c in DNA_TO_BYTE)
            if clean_line:
                sequence_lines.append(clean_line)
    
    return ''.join(sequence_lines)


def dna_to_hash_key(sequence: str) -> int:
    """
    Convert DNA sequence to integer hash key using byte mapping.
    Maps A=0, C=1, G=2, T=3 and concatenates as base-4 number.
    """
    key = 0
    for nucleotide in sequence:
        key = (key << 2) | DNA_TO_BYTE[nucleotide]
    return key


def hash_key_to_dna(key: int, length: int) -> str:
    """
    Convert integer hash key back to DNA sequence.
    """
    sequence = []
    for _ in range(length):
        sequence.append(BYTE_TO_DNA[key & 3])
        key >>= 2
    return ''.join(reversed(sequence))


def update_nucleotide_counts(sequence: str, k: int, counts: Dict[int, int]) -> None:
    """
    Update hash table of k-nucleotide keys and count values for a particular k-length.
    Uses optimized integer keys derived from DNA byte mapping.
    
    Args:
        sequence: DNA sequence string
        k: Length of nucleotide subsequences to count
        counts: Hash table (dictionary) to store k-nucleotide counts with integer keys
    """
    seq_length = len(sequence)
    
    if seq_length < k:
        return
    
    # Process all possible k-nucleotide subsequences
    for i in range(seq_length - k + 1):
        kmer = sequence[i:i + k]
        hash_key = dna_to_hash_key(kmer)
        
        # Update count in hash table - lookup and increment
        if hash_key in counts:
            counts[hash_key] += 1
        else:
            counts[hash_key] = 1


def calculate_frequencies(counts: Dict[int, int], k: int) -> List[Tuple[float, str]]:
    """
    Calculate percentage frequencies and sort by descending frequency, 
    then ascending k-nucleotide key.
    """
    total_count = sum(counts.values())
    
    # Create list of (frequency, nucleotide) tuples
    freq_list = []
    for hash_key, count in counts.items():
        nucleotide = hash_key_to_dna(hash_key, k)
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
    Count occurrences of specific nucleotide sequences using hash-based lookup.
    Returns dictionary with sequence counts.
    """
    results = {}
    
    for target in target_sequences:
        k = len(target)
        target_key = dna_to_hash_key(target)
        count = 0
        seq_length = len(sequence)
        
        # Count all occurrences using hash key comparison
        for i in range(seq_length - k + 1):
            kmer = sequence[i:i + k]
            if dna_to_hash_key(kmer) == target_key:
                count += 1
        
        results[target] = count
    
    return results


def generate_test_fasta(length: int = 25000000) -> str:
    """
    Generate a test FASTA file content for performance testing.
    Creates a pseudo-random DNA sequence of specified length.
    """
    import random
    
    nucleotides = ['A', 'C', 'G', 'T']
    sequence = ''.join(random.choices(nucleotides, k=length))
    
    fasta_content = f">THREE Homo sapiens frequency\n"
    
    # Break sequence into lines of 80 characters for proper FASTA format
    line_length = 80
    for i in range(0, len(sequence), line_length):
        fasta_content += sequence[i:i + line_length] + "\n"
    
    return fasta_content


def main():
    """Main execution function."""
    try:
        # Check if we should generate test data
        if len(sys.argv) > 1:
            if sys.argv[1] == "generate":
                length = int(sys.argv[2]) if len(sys.argv) > 2 else 25000000
                test_data = generate_test_fasta(length)
                print(test_data)
                return
        
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
        freq_1 = calculate_frequencies(counts_1, 1)
        format_frequency_output(freq_1)
        
        # Process 2-nucleotide sequences  
        print("\n2-nucleotide frequencies:")
        counts_2 = {}
        update_nucleotide_counts(dna_sequence, 2, counts_2)
        freq_2 = calculate_frequencies(counts_2, 2)
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