import sys
import collections
from collections import defaultdict
from itertools import product
from functools import lru_cache

def read_fasta() -> str:
    """Read FASTA format from stdin and extract DNA sequence THREE."""
    sequence = []
    in_sequence = False
    
    for line in sys.stdin.buffer:
        # Faster byte processing
        if line.startswith(b'>'):
            if line.startswith(b'>THREE'):
                in_sequence = True
            elif in_sequence:
                break
        elif in_sequence:
            # Remove newline and convert to uppercase bytes
            sequence.append(line.strip().upper())
    
    return b''.join(sequence)

def dna_to_bits(seq: bytes) -> bytes:
    """Convert DNA letters to bytes 0, 1, 2, 3."""
    # Using translation table for speed
    trans = bytes.maketrans(b'ACGT', b'\x00\x01\x02\x03')
    return seq.translate(trans)

def count_kmers_framed(seq_bytes: bytes, k: int, frame: int) -> dict:
    """
    Count k-nucleotides for a specific reading frame.
    Returns dictionary with integer keys (concatenated byte codes).
    """
    counts = defaultdict(int)
    step = 3  # Reading frame step
    
    for i in range(frame, len(seq_bytes) - k + 1, step):
        # Extract k-mer as bytes
        kmer_bytes = seq_bytes[i:i + k]
        
        # Convert to integer key by concatenating 2-bit codes
        key = 0
        for byte in kmer_bytes:
            key = (key << 2) | byte
        
        counts[key] += 1
    
    return counts

def combine_counts(seq_bytes: bytes, k: int) -> dict:
    """Combine counts from all reading frames."""
    total_counts = defaultdict(int)
    
    for frame in range(3):
        frame_counts = count_kmers_framed(seq_bytes, k, frame)
        for key, count in frame_counts.items():
            total_counts[key] += count
    
    return total_counts

def int_to_dna(key: int, k: int) -> str:
    """Convert integer key back to DNA string."""
    # Reverse the concatenation
    bases = []
    for _ in range(k):
        bases.append(key & 3)
        key >>= 2
    bases.reverse()
    
    # Convert 0,1,2,3 back to A,C,G,T
    trans = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
    return ''.join(trans[b] for b in bases)

def main():
    # Read and prepare sequence
    dna_seq = read_fasta()
    seq_bytes = dna_to_bits(dna_seq)
    seq_len = len(seq_bytes)
    
    # 1-nucleotide counts (simple approach, no reading frames)
    counts_1 = defaultdict(int)
    for byte in seq_bytes:
        counts_1[byte] += 1
    
    # Convert to percentages and sort
    results_1 = []
    trans = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
    for key in range(4):
        count = counts_1.get(key, 0)
        percentage = (count * 100.0) / seq_len
        results_1.append((trans[key], percentage))
    
    # Sort by percentage descending, then key ascending
    results_1.sort(key=lambda x: (-x[1], x[0]))
    
    # 2-nucleotide counts
    counts_2 = defaultdict(int)
    for i in range(len(seq_bytes) - 1):
        key = (seq_bytes[i] << 2) | seq_bytes[i + 1]
        counts_2[key] += 1
    
    # Convert and sort
    results_2 = []
    total_pairs = seq_len - 1
    for key in range(16):  # 4^2 possible 2-mers
        count = counts_2.get(key, 0)
        percentage = (count * 100.0) / total_pairs if total_pairs > 0 else 0
        dna_str = int_to_dna(key, 2)
        results_2.append((dna_str, percentage))
    
    results_2.sort(key=lambda x: (-x[1], x[0]))
    
    # Output 1 and 2 nucleotide results
    for char, perc in results_1:
        print(f"{char} {perc:.3f}")
    print()
    for dna_str, perc in results_2:
        print(f"{dna_str} {perc:.3f}")
    
    # Count specific sequences (3, 4, 6, 12, 18 nucleotides)
    targets = [
        ("GGT", 3),
        ("GGTA", 4),
        ("GGTATT", 6),
        ("GGTATTTTAATT", 12),
        ("GGTATTTTAATTTATAGT", 18)
    ]
    
    print()
    for target_dna, k in targets:
        # Convert target to integer key
        target_bytes = dna_to_bits(target_dna.encode())
        target_key = 0
        for byte in target_bytes:
            target_key = (target_key << 2) | byte
        
        # Count occurrences in all reading frames
        counts = combine_counts(seq_bytes, k)
        count = counts.get(target_key, 0)
        print(f"{count}\t{target_dna}")

if __name__ == "__main__":
    main()