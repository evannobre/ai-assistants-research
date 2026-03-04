#!/usr/bin/env python3
"""
K-Nucleotide Simulation Algorithm
Optimized for Ubuntu 24.04.2 LTS with 16GB RAM and 30GB SSD

This implementation uses native Python libraries and focuses on memory efficiency
for k-nucleotide frequency analysis of DNA sequences.
"""

import sys
import os
import gc
from collections import defaultdict, Counter
from itertools import islice
import mmap
import argparse
import time
from typing import Dict, Iterator, Tuple, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class KNucleotideAnalyzer:
    """
    Memory-efficient k-nucleotide frequency analyzer using native Python libraries.
    Designed for systems with limited RAM (16GB) and SSD storage (30GB).
    """
    
    def __init__(self, max_memory_mb: int = 12000):
        """
        Initialize analyzer with memory constraints.
        
        Args:
            max_memory_mb: Maximum memory usage in MB (default: 12GB out of 16GB)
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.nucleotides = set('ACGT')
        self.complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    
    def memory_mapped_file_reader(self, filepath: str) -> Iterator[str]:
        """
        Memory-efficient file reading using mmap for large FASTA files.
        
        Args:
            filepath: Path to FASTA file
            
        Yields:
            Clean nucleotide sequences (no headers, uppercase)
        """
        try:
            with open(filepath, 'rb') as file:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    current_sequence = []
                    
                    for line in iter(mmapped_file.readline, b""):
                        line = line.decode('utf-8', errors='ignore').strip()
                        
                        if line.startswith('>'):
                            # New sequence header - yield previous sequence if exists
                            if current_sequence:
                                yield ''.join(current_sequence).upper()
                                current_sequence = []
                        else:
                            # Filter out non-nucleotide characters
                            clean_line = ''.join(c for c in line.upper() if c in self.nucleotides)
                            if clean_line:
                                current_sequence.append(clean_line)
                    
                    # Yield final sequence
                    if current_sequence:
                        yield ''.join(current_sequence).upper()
                        
        except IOError as e:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            return
    
    def generate_kmers_streaming(self, sequence: str, k: int, chunk_size: int = 1000000) -> Iterator[str]:
        """
        Generate k-mers from sequence using streaming approach to minimize memory usage.
        
        Args:
            sequence: DNA sequence string
            k: Length of k-mers
            chunk_size: Size of chunks to process at once
            
        Yields:
            k-mer strings
        """
        if len(sequence) < k:
            return
        
        # Process sequence in overlapping chunks to handle memory constraints
        for start in range(0, len(sequence) - k + 1, chunk_size):
            end = min(start + chunk_size + k - 1, len(sequence))
            chunk = sequence[start:end]
            
            # Generate k-mers from current chunk
            for i in range(len(chunk) - k + 1):
                kmer = chunk[i:i + k]
                if len(kmer) == k and all(c in self.nucleotides for c in kmer):
                    yield kmer
            
            # Force garbage collection for memory management
            if start % (chunk_size * 10) == 0:
                gc.collect()
    
    def count_kmers_parallel(self, sequence: str, k: int, num_threads: int = 4) -> Counter:
        """
        Count k-mers using parallel processing with thread pool.
        
        Args:
            sequence: DNA sequence
            k: Length of k-mers
            num_threads: Number of worker threads
            
        Returns:
            Counter object with k-mer frequencies
        """
        if len(sequence) < k:
            return Counter()
        
        # Calculate chunk size based on available memory and threads
        chunk_size = max(1000000, len(sequence) // (num_threads * 4))
        
        def count_chunk_kmers(chunk_data: Tuple[str, int, int]) -> Counter:
            """Count k-mers in a sequence chunk."""
            chunk_seq, start_pos, chunk_k = chunk_data
            local_counter = Counter()
            
            for i in range(len(chunk_seq) - chunk_k + 1):
                kmer = chunk_seq[i:i + chunk_k]
                if len(kmer) == chunk_k and all(c in self.nucleotides for c in kmer):
                    local_counter[kmer] += 1
            
            return local_counter
        
        # Prepare chunks with overlap to ensure no k-mers are missed
        chunks = []
        for start in range(0, len(sequence) - k + 1, chunk_size):
            end = min(start + chunk_size + k - 1, len(sequence))
            chunk = sequence[start:end]
            chunks.append((chunk, start, k))
        
        # Process chunks in parallel
        total_counter = Counter()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_chunk = {executor.submit(count_chunk_kmers, chunk): chunk for chunk in chunks}
            
            for future in as_completed(future_to_chunk):
                try:
                    chunk_counter = future.result()
                    total_counter.update(chunk_counter)
                except Exception as e:
                    print(f"Error processing chunk: {e}", file=sys.stderr)
        
        return total_counter
    
    def analyze_kmer_frequencies(self, filepath: str, k_values: list, 
                               output_file: Optional[str] = None, 
                               num_threads: int = 4) -> Dict[int, Counter]:
        """
        Analyze k-mer frequencies for multiple k values from FASTA file.
        
        Args:
            filepath: Path to FASTA file
            k_values: List of k values to analyze
            output_file: Optional output file path
            num_threads: Number of threads for parallel processing
            
        Returns:
            Dictionary mapping k values to their frequency counters
        """
        results = {}
        
        print(f"Analyzing k-mer frequencies for k values: {k_values}")
        print(f"Using {num_threads} threads for parallel processing")
        
        for sequence in self.memory_mapped_file_reader(filepath):
            print(f"Processing sequence of length: {len(sequence):,}")
            
            for k in k_values:
                start_time = time.time()
                print(f"Analyzing {k}-mers...")
                
                # Count k-mers using parallel processing
                kmer_counts = self.count_kmers_parallel(sequence, k, num_threads)
                
                if k in results:
                    results[k].update(kmer_counts)
                else:
                    results[k] = kmer_counts
                
                elapsed = time.time() - start_time
                print(f"  Found {len(kmer_counts):,} unique {k}-mers in {elapsed:.2f}s")
                
                # Force garbage collection
                del kmer_counts
                gc.collect()
        
        # Save results if output file specified
        if output_file:
            self.save_results(results, output_file)
        
        return results
    
    def get_top_kmers(self, kmer_counter: Counter, top_n: int = 10) -> list:
        """
        Get top N most frequent k-mers.
        
        Args:
            kmer_counter: Counter with k-mer frequencies
            top_n: Number of top k-mers to return
            
        Returns:
            List of tuples (kmer, frequency) sorted by frequency
        """
        return kmer_counter.most_common(top_n)
    
    def calculate_gc_content(self, sequence: str) -> float:
        """
        Calculate GC content of sequence.
        
        Args:
            sequence: DNA sequence
            
        Returns:
            GC content as percentage
        """
        if not sequence:
            return 0.0
        
        gc_count = sequence.count('G') + sequence.count('C')
        return (gc_count / len(sequence)) * 100
    
    def reverse_complement(self, sequence: str) -> str:
        """
        Generate reverse complement of DNA sequence.
        
        Args:
            sequence: DNA sequence
            
        Returns:
            Reverse complement sequence
        """
        return ''.join(self.complement_map.get(base, base) for base in reversed(sequence))
    
    def save_results(self, results: Dict[int, Counter], output_file: str):
        """
        Save analysis results to file.
        
        Args:
            results: Dictionary of k-mer analysis results
            output_file: Output file path
        """
        try:
            with open(output_file, 'w') as f:
                f.write("K-Nucleotide Frequency Analysis Results\n")
                f.write("=" * 50 + "\n\n")
                
                for k in sorted(results.keys()):
                    counter = results[k]
                    f.write(f"K-mer length: {k}\n")
                    f.write(f"Total unique k-mers: {len(counter):,}\n")
                    f.write(f"Total k-mer count: {sum(counter.values()):,}\n")
                    f.write(f"Top 20 most frequent {k}-mers:\n")
                    
                    for kmer, count in counter.most_common(20):
                        f.write(f"  {kmer}: {count:,}\n")
                    
                    f.write("\n" + "-" * 30 + "\n\n")
                
            print(f"Results saved to: {output_file}")
            
        except IOError as e:
            print(f"Error saving results: {e}", file=sys.stderr)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="K-Nucleotide Frequency Analysis")
    parser.add_argument("input_file", help="Input FASTA file path")
    parser.add_argument("-k", "--k-values", nargs="+", type=int, default=[3, 4, 5],
                       help="K-mer lengths to analyze (default: 3 4 5)")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-t", "--threads", type=int, default=4,
                       help="Number of threads (default: 4)")
    parser.add_argument("--memory-limit", type=int, default=12000,
                       help="Memory limit in MB (default: 12000)")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = KNucleotideAnalyzer(max_memory_mb=args.memory_limit)
    
    # Run analysis
    start_time = time.time()
    results = analyzer.analyze_kmer_frequencies(
        args.input_file, 
        args.k_values, 
        args.output,
        args.threads
    )
    
    total_time = time.time() - start_time
    
    # Print summary
    print(f"\nAnalysis completed in {total_time:.2f} seconds")
    print("Summary:")
    for k in sorted(results.keys()):
        counter = results[k]
        print(f"  {k}-mers: {len(counter):,} unique, {sum(counter.values()):,} total")


if __name__ == "__main__":
    main()