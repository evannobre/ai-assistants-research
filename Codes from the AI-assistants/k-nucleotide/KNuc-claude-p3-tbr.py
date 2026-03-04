#!/usr/bin/env python3
"""
K-nucleotide simulation using native Python hash tables (dict).
Reads FASTA format, extracts DNA sequence THREE, and counts k-nucleotide frequencies.
"""

import sys
from collections import defaultdict


def read_fasta_sequence(name):
    """Read FASTA format file and extract the sequence with given name."""
    lines = sys.stdin.readlines()
    
    # Find the start of the desired sequence
    found = False
    sequence_lines = []
    
    for line in lines:
        if line.startswith('>'):
            if found:
                # We've reached the next sequence, stop
                break
            if name in line:
                found = True
                continue
        elif found:
            sequence_lines.append(line.strip().upper())
    
    return ''.join(sequence_lines)


def update_frequencies(sequence, length, frame_offset=0):
    """
    Update hash table with k-nucleotide counts for a given length.
    Processes a single reading frame starting at frame_offset.
    Uses native Python dict (hash table) to accumulate counts.
    """
    frequencies = defaultdict(int)
    seq_len = len(sequence)
    
    # Process from frame_offset to end of sequence
    for i in range(frame_offset, seq_len - length + 1):
        nucleotide = sequence[i:i + length]
        # Lookup current count and update (increment by 1)
        frequencies[nucleotide] += 1
    
    return frequencies


def combine_all_frames(sequence, length):
    """
    Combine k-nucleotide counts from all reading frames.
    This ensures we count all occurrences regardless of frame.
    """
    combined = defaultdict(int)
    
    # Process all reading frames (0 to length-1)
    for frame in range(length):
        frame_freq = update_frequencies(sequence, length, frame)
        # Merge this frame's counts into combined hash table
        for nucleotide, count in frame_freq.items():
            combined[nucleotide] += count
    
    return combined


def calculate_frequencies(sequence, length):
    """Calculate frequencies for all reading frames combined."""
    # Get counts from all frames
    frequencies = combine_all_frames(sequence, length)
    
    total = sum(frequencies.values())
    
    # Create list of (nucleotide, percentage) tuples
    result = []
    for nucleotide, count in frequencies.items():
        percentage = (count * 100.0) / total
        result.append((nucleotide, percentage))
    
    # Sort by descending frequency, then ascending nucleotide
    result.sort(key=lambda x: (-x[1], x[0]))
    
    return result


def write_frequencies(sequence, length):
    """Write frequencies in required format."""
    frequencies = calculate_frequencies(sequence, length)
    for nucleotide, percentage in frequencies:
        print(f"{nucleotide} {percentage:.3f}")
    print()


def count_specific(sequence, nucleotide_sequence):
    """Count occurrences of a specific nucleotide sequence."""
    length = len(nucleotide_sequence)
    # Use the update_frequencies function with all frames combined
    frequencies = combine_all_frames(sequence, length)
    count = frequencies[nucleotide_sequence]
    return count


def main():
    # Read DNA sequence THREE from stdin
    sequence = read_fasta_sequence('THREE')
    
    # Count and write 1-nucleotide frequencies
    write_frequencies(sequence, 1)
    
    # Count and write 2-nucleotide frequencies
    write_frequencies(sequence, 2)
    
    # Count specific sequences
    specific_sequences = [
        'GGT',
        'GGTA',
        'GGTATT',
        'GGTATTTTAATT',
        'GGTATTTTAATTTATAGT'
    ]
    
    for seq in specific_sequences:
        count = count_specific(sequence, seq)
        print(f"{count}\t{seq}")


if __name__ == '__main__':
    main()
