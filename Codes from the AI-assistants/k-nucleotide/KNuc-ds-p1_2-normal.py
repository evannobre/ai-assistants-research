import sys
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

def read_sequence_simple(filename: str) -> str:
    """Simplified FASTA reader."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find sequence markers
    seq_starts = [i for i, line in enumerate(lines) if line.startswith('>')]
    
    # Take third sequence or first if not enough
    seq_index = 2 if len(seq_starts) >= 3 else 0
    start = seq_starts[seq_index] + 1
    
    # Find end of sequence
    end = seq_starts[seq_index + 1] if seq_index + 1 < len(seq_starts) else len(lines)
    
    # Join sequence lines
    sequence = ''.join(line.strip().upper() for line in lines[start:end])
    return sequence

def optimized_count(seq: str, k: int) -> Dict[str, int]:
    """Optimized counting using str.count for small k values."""
    if k <= 4:
        # For small k, we can count all possible combinations
        counts = {}
        bases = ['A', 'C', 'G', 'T']
        
        # Generate all possible k-mers
        from itertools import product
        all_kmers = [''.join(p) for p in product(bases, repeat=k)]
        
        for kmer in all_kmers:
            count = 0
            pos = -1
            while True:
                pos = seq.find(kmer, pos + 1)
                if pos == -1:
                    break
                count += 1
            if count > 0:
                counts[kmer] = count
    else:
        # For larger k, use sliding window
        counts = {}
        for i in range(len(seq) - k + 1):
            kmer = seq[i:i + k]
            counts[kmer] = counts.get(kmer, 0) + 1
    
    return counts

def main_optimized():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <input_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    sequence = read_sequence_simple(filename)
    
    # Pre-compute for all required k values
    required_ks = {1, 2, 3, 4, 6, 12, 18}
    results = {}
    
    for k in required_ks:
        results[k] = optimized_count(sequence, k)
    
    # Print specific counts (benchmark output)
    specific_patterns = [
        'GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT'
    ]
    
    for pattern in specific_patterns:
        k = len(pattern)
        count = results.get(k, {}).get(pattern, 0)
        print(f"{count}\t{pattern}")
    
    print()
    
    # Print frequency tables
    for k in [1, 2]:
        counts = results[k]
        total = sum(counts.values())
        
        # Sort by frequency then alphabetically
        sorted_items = sorted(
            counts.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        for kmer, count in sorted_items:
            freq = (count / total) * 100
            print(f"{kmer} {freq:.3f}")
        
        if k == 1:
            print()

if __name__ == "__main__":
    main_optimized()