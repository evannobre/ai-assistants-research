#!/usr/bin/env python3
"""
K-nucleotide frequency analysis using Python's native data structures
Optimized for performance with built-in libraries
"""

from collections import Counter, defaultdict
import sys
from operator import itemgetter

def read_fasta_sequence(file_path=None):
    """
    Read DNA sequence from FASTA file or stdin
    Returns cleaned DNA sequence (uppercase, no whitespace)
    """
    if file_path:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    
    # Skip header line(s) starting with '>'
    sequence_lines = [line.strip() for line in lines if not line.startswith('>')]
    return ''.join(sequence_lines).upper()

def generate_kmers(sequence, k):
    """
    Generate all k-mers from sequence using Python's slicing
    Memory efficient generator approach
    """
    seq_len = len(sequence)
    if k > seq_len:
        return
    
    # Use range for efficient iteration
    for i in range(seq_len - k + 1):
        yield sequence[i:i + k]

def count_kmers_counter(sequence, k):
    """
    Count k-mers using collections.Counter (most Pythonic)
    """
    return Counter(generate_kmers(sequence, k))

def count_kmers_dict(sequence, k):
    """
    Count k-mers using native dict with get() method
    Slightly more memory efficient for large datasets
    """
    counts = {}
    seq_len = len(sequence)
    
    for i in range(seq_len - k + 1):
        kmer = sequence[i:i + k]
        counts[kmer] = counts.get(kmer, 0) + 1
    
    return counts

def calculate_frequencies(kmer_counts, total_count):
    """
    Calculate frequency percentages
    Returns list of (kmer, frequency) tuples sorted by frequency desc, then alphabetically
    """
    freq_list = []
    for kmer, count in kmer_counts.items():
        frequency = (count * 100.0) / total_count
        freq_list.append((kmer, frequency))
    
    # Sort by frequency (descending), then by kmer (ascending)
    return sorted(freq_list, key=lambda x: (-x[1], x[0]))

def find_specific_sequence_count(sequence, target):
    """
    Count occurrences of specific nucleotide sequence
    Uses string.count() method for optimal performance
    """
    return sequence.count(target)

def analyze_knucleotide(sequence, k_values, specific_sequences=None):
    """
    Main analysis function
    
    Args:
        sequence: DNA sequence string
        k_values: list of k values to analyze
        specific_sequences: list of specific sequences to count
    
    Returns:
        dict with analysis results
    """
    results = {}
    
    # Analyze each k-value
    for k in k_values:
        print(f"\nAnalyzing {k}-nucleotides...")
        
        # Count k-mers using Counter (fastest for most cases)
        kmer_counts = count_kmers_counter(sequence, k)
        total_kmers = sum(kmer_counts.values())
        
        # Calculate frequencies
        frequencies = calculate_frequencies(kmer_counts, total_kmers)
        
        results[k] = {
            'counts': kmer_counts,
            'frequencies': frequencies,
            'total': total_kmers
        }
        
        # Display top results
        print(f"Total {k}-mers: {total_kmers}")
        for kmer, freq in frequencies[:10]:  # Top 10
            print(f"{kmer} {freq:.3f}")
    
    # Count specific sequences if provided
    if specific_sequences:
        print(f"\nSpecific sequence counts:")
        for seq in specific_sequences:
            count = find_specific_sequence_count(sequence, seq)
            results[f'specific_{seq}'] = count
            print(f"{seq}\t{count}")
    
    return results

def benchmark_methods(sequence, k=2, iterations=1):
    """
    Compare performance of different counting methods
    """
    import time
    
    print(f"\nBenchmarking different methods for {k}-mers ({iterations} iterations):")
    
    # Method 1: Counter
    start = time.time()
    for _ in range(iterations):
        counts1 = count_kmers_counter(sequence, k)
    time1 = time.time() - start
    print(f"Counter method: {time1:.4f}s")
    
    # Method 2: dict.get()
    start = time.time()
    for _ in range(iterations):
        counts2 = count_kmers_dict(sequence, k)
    time2 = time.time() - start
    print(f"Dict.get() method: {time2:.4f}s")
    
    # Verify results are identical
    assert counts1 == counts2, "Methods produce different results!"
    print("✓ All methods produce identical results")

# Example usage and test function
def main():
    """
    Example usage of the k-nucleotide algorithm
    """
    # Sample DNA sequence (you can replace with file input)
    sample_sequence = """
    ATGCATGCATGCATGCATGCATGCATGCATGCATGC
    GCATGCATGCATGCATGCATGCATGCATGCATGCAT
    CATGCATGCATGCATGCATGCATGCATGCATGCATG
    ATGCATGCATGCATGCATGCATGCATGCATGCATGC
    """.replace('\n', '').replace(' ', '').upper()
    
    print(f"Sequence length: {len(sample_sequence)}")
    print(f"Sample: {sample_sequence[:50]}...")
    
    # Analyze different k-values
    k_values = [1, 2, 3, 6]
    specific_sequences = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    
    results = analyze_knucleotide(sample_sequence, k_values, specific_sequences)
    
    # Optional: benchmark different methods
    if len(sample_sequence) > 1000:  # Only for larger sequences
        benchmark_methods(sample_sequence, k=2, iterations=10)

if __name__ == "__main__":
    main()