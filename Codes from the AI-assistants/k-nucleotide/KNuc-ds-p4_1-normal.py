import sys
from collections import defaultdict
import mmap
import os
from functools import partial

def read_fasta():
    """Read FASTA from stdin and extract DNA sequence THREE"""
    data = sys.stdin.buffer.read()
    
    # Find sequence THREE
    lines = data.split(b'\n')
    sequence = bytearray()
    in_sequence = False
    
    for line in lines:
        if line.startswith(b'>'):
            if b'THREE' in line:
                in_sequence = True
                continue
            elif in_sequence:
                break
        elif in_sequence:
            # Convert to uppercase and remove whitespace
            clean_line = line.strip().upper()
            for char in clean_line:
                if char in b"ACGT":
                    sequence.append(char)
    
    return sequence

def update_counts(seq, k, counts, frame=0):
    """Update hash table with k-nucleotide counts for a specific reading frame"""
    length = len(seq)
    for i in range(frame, length - k + 1, 1):
        key = seq[i:i+k]
        counts[key] += 1

def byte_key_to_str(key):
    """Convert bytearray key to string"""
    return key.decode('ascii')

def main():
    # Read and extract sequence
    sequence = read_fasta()
    seq_len = len(sequence)
    
    # Count 1-nucleotide sequences
    counts_1 = defaultdict(int)
    update_counts(sequence, 1, counts_1, 0)
    
    # Count 2-nucleotide sequences
    counts_2 = defaultdict(int)
    update_counts(sequence, 2, counts_2, 0)
    
    # Convert to lists and sort
    freq_1 = [(byte_key_to_str(k), v, v/seq_len*100) 
              for k, v in counts_1.items()]
    freq_1.sort(key=lambda x: (-x[1], x[0]))
    
    freq_2 = [(byte_key_to_str(k), v, v/(seq_len-1)*100) 
              for k, v in counts_2.items()]
    freq_2.sort(key=lambda x: (-x[1], x[0]))
    
    # Print 1-nucleotide results
    for k, count, percent in freq_1:
        print(f"{k} {percent:.3f}")
    print()
    
    # Print 2-nucleotide results
    for k, count, percent in freq_2:
        print(f"{k} {percent:.3f}")
    print()
    
    # Count specific k-nucleotide sequences
    k_values = [3, 4, 6, 12, 18]
    target_sequences = [b'GGT', b'GGTA', b'GGTATT', 
                       b'GGTATTTTAATT', b'GGTATTTTAATTTATAGT']
    
    for k, target in zip(k_values, target_sequences):
        counts_k = defaultdict(int)
        update_counts(sequence, k, counts_k, 0)
        count = counts_k.get(target, 0)
        print(f"{count}\t{target.decode('ascii')}")

if __name__ == "__main__":
    main()