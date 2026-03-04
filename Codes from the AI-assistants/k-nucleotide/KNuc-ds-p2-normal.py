#!/usr/bin/env python3
"""
k-nucleotide simulation optimized for Ubuntu 24.04.4 with 8GB RAM
Uses native Python libraries and avoids custom hash tables
"""

import sys
import gzip
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from itertools import islice
import mmap
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def read_sequence(file_path: str) -> str:
    """
    Efficiently read DNA sequence from FASTA file using memory mapping.
    Handles both plain text and gzipped files.
    """
    if file_path.endswith('.gz'):
        with gzip.open(file_path, 'rt') as f:
            lines = []
            # Skip FASTA header lines
            for line in f:
                if line.startswith('>'):
                    if lines:  # We've already started reading sequence
                        break
                    continue
                lines.append(line.strip())
            # Read remaining sequence
            for line in f:
                if not line.startswith('>'):
                    lines.append(line.strip())
            return ''.join(lines)
    else:
        # Use memory mapping for large files
        with open(file_path, 'r') as f:
            # Check if file is small enough to read directly
            file_size = os.path.getsize(file_path)
            if file_size < 100 * 1024 * 1024:  # < 100MB
                lines = []
                in_sequence = False
                for line in f:
                    if line.startswith('>'):
                        if in_sequence:
                            break
                        in_sequence = True
                        continue
                    if in_sequence:
                        lines.append(line.strip())
                return ''.join(lines)
            else:
                # Use mmap for larger files
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Extract sequence using regex to skip headers
                    mm.seek(0)
                    data = mm.read().decode('utf-8')
                    # Find first sequence after first header
                    match = re.search(r'>[^\n]*\n([A-Za-z\n]+)', data)
                    if match:
                        sequence = match.group(1).replace('\n', '')
                        return sequence
                    return ""

def generate_kmers(sequence: str, k: int) -> List[str]:
    """
    Generate all k-mers from sequence using generator for memory efficiency.
    """
    return [sequence[i:i+k] for i in range(len(sequence) - k + 1)]

def count_kmers_parallel(sequence: str, k: int, chunk_size: int = 1000000) -> Dict[str, int]:
    """
    Count k-mers using parallel processing for better performance.
    """
    if len(sequence) < 100000:  # Small sequence, use simple approach
        kmers = generate_kmers(sequence, k)
        return dict(Counter(kmers))
    
    # For large sequences, process in parallel chunks
    def process_chunk(start: int) -> Counter:
        end = min(start + chunk_size + k - 1, len(sequence))
        chunk_seq = sequence[start:end]
        kmers = generate_kmers(chunk_seq, k)
        return Counter(kmers)
    
    results = Counter()
    chunk_starts = range(0, len(sequence) - k + 1, chunk_size)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_chunk, start) for start in chunk_starts]
        for future in as_completed(futures):
            results.update(future.result())
    
    return dict(results)

def calculate_frequencies(sequence: str, k_values: List[int] = None) -> Dict[int, Dict[str, float]]:
    """
    Calculate frequencies for different k values.
    Returns dictionary with k-mer frequencies.
    """
    if k_values is None:
        k_values = [1, 2, 3, 4, 6, 12, 18]
    
    frequencies = {}
    
    for k in k_values:
        if k > len(sequence):
            continue
            
        counts = count_kmers_parallel(sequence, k)
        total = sum(counts.values())
        
        # Calculate frequencies
        freq_dict = {kmer: (count / total) * 100 for kmer, count in counts.items()}
        
        # Sort by frequency descending, then by k-mer ascending
        sorted_freq = dict(sorted(
            freq_dict.items(),
            key=lambda x: (-x[1], x[0])
        ))
        
        frequencies[k] = sorted_freq
    
    return frequencies

def find_most_frequent(sequence: str, k: int, top_n: int = 5) -> List[Tuple[str, int, float]]:
    """
    Find the most frequent k-mers.
    Returns list of (kmer, count, frequency) tuples.
    """
    counts = count_kmers_parallel(sequence, k)
    total = sum(counts.values())
    
    # Get top N most frequent
    most_common = Counter(counts).most_common(top_n)
    
    results = []
    for kmer, count in most_common:
        frequency = (count / total) * 100
        results.append((kmer, count, frequency))
    
    return results

def benchmark_sequence(sequence: str) -> Dict[str, float]:
    """
    Perform benchmark analysis on the sequence.
    """
    import time
    
    benchmark_results = {}
    
    # Benchmark different k values
    k_values = [1, 2, 3, 4, 6, 12, 18]
    
    for k in k_values:
        if k > len(sequence):
            continue
            
        start_time = time.time()
        counts = count_kmers_parallel(sequence, k)
        elapsed = time.time() - start_time
        
        benchmark_results[f'k={k}'] = {
            'time_seconds': elapsed,
            'unique_kmers': len(counts),
            'total_kmers': sum(counts.values())
        }
    
    return benchmark_results

def print_results(sequence: str, file_path: str):
    """
    Print formatted results similar to benchmark requirements.
    """
    print(f"Processing: {file_path}")
    print(f"Sequence length: {len(sequence):,} bp")
    print()
    
    # 1. Single nucleotide frequencies
    print("1-nucleotide frequencies:")
    counts_1 = count_kmers_parallel(sequence, 1)
    total = sum(counts_1.values())
    for base in sorted(['A', 'C', 'G', 'T']):
        count = counts_1.get(base, 0)
        freq = (count / total) * 100
        print(f"{base}: {count:8,d} ({freq:6.2f}%)")
    print()
    
    # 2. Most frequent 2-mers
    print("Most frequent 2-mers:")
    most_freq_2 = find_most_frequent(sequence, 2, 5)
    for kmer, count, freq in most_freq_2:
        print(f"{kmer}: {count:8,d} ({freq:6.2f}%)")
    print()
    
    # 3. Specific k-mer counts (as in typical benchmark)
    specific_kmers = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    for kmer in specific_kmers:
        k = len(kmer)
        if k <= len(sequence):
            counts = count_kmers_parallel(sequence, k)
            count = counts.get(kmer, 0)
            print(f"{kmer}\t{count}")
    print()
    
    # Memory usage info
    import psutil
    process = psutil.Process()
    mem_info = process.memory_info()
    print(f"Memory usage: {mem_info.rss / 1024 / 1024:.1f} MB")

def main():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <dna_file>")
        print("Supported formats: .fa, .fasta, .fna, .gz (gzipped)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    try:
        # Read sequence
        print(f"Reading sequence from {file_path}...")
        sequence = read_sequence(file_path)
        sequence = sequence.upper()  # Ensure uppercase
        
        if not sequence:
            print("Error: No sequence data found in file")
            sys.exit(1)
        
        # Validate sequence contains only valid DNA bases
        valid_bases = set('ACGTN')
        if not set(sequence).issubset(valid_bases):
            print("Warning: Sequence contains non-standard bases")
            # Filter to only valid bases for accurate counting
            sequence = ''.join(base for base in sequence if base in valid_bases)
        
        print_results(sequence, file_path)
        
        # Optional: Run benchmark
        if len(sequence) < 1000000:  # Only benchmark for reasonably sized sequences
            print("\nBenchmark results:")
            benchmark = benchmark_sequence(sequence)
            for k, stats in benchmark.items():
                print(f"{k}: {stats['time_seconds']:.3f}s, "
                      f"{stats['unique_kmers']:,} unique, "
                      f"{stats['total_kmers']:,} total")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()