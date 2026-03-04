import sys
import re
from collections import Counter
from typing import Dict, List, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor

def read_sequence(filename: str) -> str:
    """Read FASTA format and extract the THIRD sequence (as per benchmark spec)."""
    sequences = []
    current_seq = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_seq:
                    sequences.append(''.join(current_seq))
                    current_seq = []
            else:
                current_seq.append(line.upper())
        if current_seq:
            sequences.append(''.join(current_seq))
    
    # According to benchmark spec, we use the third sequence
    return sequences[2] if len(sequences) >= 3 else sequences[0]

def count_sequences(seq: str, k: int) -> Dict[str, int]:
    """Count all k-length subsequences using Python's native dict."""
    counts = {}
    for i in range(len(seq) - k + 1):
        subseq = seq[i:i + k]
        counts[subseq] = counts.get(subseq, 0) + 1
    return counts

def calculate_frequencies(counts: Dict[str, int]) -> List[Tuple[str, float]]:
    """Calculate frequencies from counts."""
    total = sum(counts.values())
    return [(seq, (count / total) * 100) for seq, count in counts.items()]

def sort_results(results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """Sort by frequency descending, then alphabetically ascending."""
    return sorted(results, key=lambda x: (-x[1], x[0]))

def parallel_count(seq: str, k_values: List[int]) -> Dict[int, Dict[str, int]]:
    """Count for multiple k values in parallel."""
    results = {}
    
    with ThreadPoolExecutor(max_workers=len(k_values)) as executor:
        futures = {executor.submit(count_sequences, seq, k): k for k in k_values}
        for future in futures:
            k = futures[future]
            results[k] = future.result()
    
    return results

def print_results(seq: str, results: Dict[int, Dict[str, int]]):
    """Print results in the format required by the benchmark."""
    
    # 1. Print counts for specific sequences
    specific_seqs = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    for pattern in specific_seqs:
        if len(pattern) in results:
            count = results[len(pattern)].get(pattern, 0)
            print(f"{count}\t{pattern}")
    
    print()
    
    # 2. Print frequency tables for k=1,2
    for k in [1, 2]:
        if k in results:
            frequencies = calculate_frequencies(results[k])
            sorted_freq = sort_results(frequencies)
            
            for seq_pattern, freq in sorted_freq:
                print(f"{seq_pattern} {freq:.3f}")
            print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <input_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read and prepare sequence
    sequence = read_sequence(filename)
    
    # Define k values to analyze (per benchmark spec)
    k_values = [1, 2, 3, 4, 6, 12, 18]
    
    # Count all subsequences
    results = parallel_count(sequence, k_values)
    
    # Print results
    print_results(sequence, results)

if __name__ == "__main__":
    main()