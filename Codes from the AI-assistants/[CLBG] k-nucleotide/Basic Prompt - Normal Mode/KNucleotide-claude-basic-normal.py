#!/usr/bin/env python3
"""
K-nucleotide frequency analysis implementation
Reads FASTA format from stdin and analyzes DNA sequence THREE
"""

import sys
from collections import defaultdict
import operator

def read_fasta_sequence_three(file_handle):
    """Read FASTA format and extract DNA sequence THREE"""
    sequences = {}
    current_seq = None
    current_data = []
    
    for line in file_handle:
        line = line.strip()
        if line.startswith('>'):
            if current_seq is not None:
                sequences[current_seq] = ''.join(current_data)
            current_seq = line[1:]  # Remove '>' prefix
            current_data = []
        else:
            current_data.append(line.upper())
    
    # Don't forget the last sequence
    if current_seq is not None:
        sequences[current_seq] = ''.join(current_data)
    
    # Extract sequence THREE
    for seq_name, seq_data in sequences.items():
        if 'THREE' in seq_name.upper():
            return seq_data
    
    # If no sequence named THREE found, return the last/longest sequence
    if sequences:
        return max(sequences.values(), key=len)
    
    return ""

def update_hash_table(hash_table, dna_sequence, k):
    """
    Update hash table with k-nucleotide counts for all reading frames
    Args:
        hash_table: dictionary to store k-nucleotide counts
        dna_sequence: DNA sequence string
        k: length of nucleotide subsequences
    """
    seq_len = len(dna_sequence)
    
    # Process all possible k-nucleotides (all reading frames)
    for i in range(seq_len - k + 1):
        k_nucleotide = dna_sequence[i:i + k]
        # Use defaultdict to automatically initialize counts to 0
        hash_table[k_nucleotide] += 1

def calculate_frequencies(hash_table, total_count):
    """Calculate percentage frequencies and sort by descending frequency, then ascending key"""
    freq_list = []
    for nucleotide, count in hash_table.items():
        percentage = (count * 100.0) / total_count
        freq_list.append((percentage, nucleotide, count))
    
    # Sort by descending frequency, then ascending nucleotide key
    freq_list.sort(key=lambda x: (-x[0], x[1]))
    return freq_list

def print_frequency_table(hash_table, k):
    """Print frequency table sorted by descending frequency"""
    total_count = sum(hash_table.values())
    if total_count == 0:
        return
        
    freq_list = calculate_frequencies(hash_table, total_count)
    
    for percentage, nucleotide, count in freq_list:
        print(f"{nucleotide} {percentage:.3f}")
    print()

def print_specific_counts(hash_table, targets):
    """Print counts for specific nucleotide sequences"""
    for target in targets:
        count = hash_table.get(target, 0)
        print(f"{count}\t{target}")

def main():
    # Read DNA sequence THREE from stdin
    dna_sequence = read_fasta_sequence_three(sys.stdin)
    
    if not dna_sequence:
        print("No DNA sequence found", file=sys.stderr)
        return
    
    # Hash tables for different k-nucleotide lengths
    hash_tables = {}
    
    # Count 1-nucleotide and 2-nucleotide sequences
    for k in [1, 2]:
        hash_tables[k] = defaultdict(int)
        update_hash_table(hash_tables[k], dna_sequence, k)
        print_frequency_table(hash_tables[k], k)
    
    # Count 3, 4, 6, 12, and 18-nucleotide sequences for specific targets
    target_sequences = {
        3: ["GGT"],
        4: ["GGTA"],
        6: ["GGTATT"],
        12: ["GGTATTTTAATT"],
        18: ["GGTATTTTAATTTATAGT"]
    }
    
    for k in [3, 4, 6, 12, 18]:
        hash_tables[k] = defaultdict(int)
        update_hash_table(hash_tables[k], dna_sequence, k)
        
        if k in target_sequences:
            print_specific_counts(hash_tables[k], target_sequences[k])

if __name__ == "__main__":
    main()