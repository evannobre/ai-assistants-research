import sys
import mmap
import re
from collections import defaultdict
from multiprocessing import Pool
from functools import partial

def read_sequence(filename):
    """Read DNA sequence using memory-mapped file for efficiency"""
    with open(filename, 'r') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # Skip header lines
            while mm.readline().startswith(b'>'):
                pass
            # Read sequence (uppercase, remove whitespace)
            sequence = mm.read().upper()
            sequence = re.sub(br'[^ACGT]', b'', sequence)
            return sequence.decode('ascii')

def count_sequences(sequence, k):
    """Count k-length sequences using native dictionary"""
    counts = defaultdict(int)
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
    return counts

def parallel_count(sequence, k_values):
    """Parallel counting for different k values"""
    with Pool() as pool:
        func = partial(count_sequences, sequence)
        results = pool.map(func, k_values)
    return dict(zip(k_values, results))

def write_results(results, output_file):
    """Write results in required format"""
    with open(output_file, 'w') as f:
        for k, counts in sorted(results.items()):
            total = sum(counts.values())
            sorted_kmers = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            f.write(f"Results for k={k} (total {total} sequences):\n")
            for kmer, count in sorted_kmers:
                f.write(f"{kmer} {count}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python knucleotide.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file, output_file = sys.argv[1], sys.argv[2]
    
    try:
        # Read sequence efficiently
        sequence = read_sequence(input_file)
        
        # Count for common k values (1, 2, 3-6, etc.)
        k_values = [1, 2] + list(range(3, 7))
        
        # Parallel counting
        results = parallel_count(sequence, k_values)
        
        # Write results
        write_results(results, output_file)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()