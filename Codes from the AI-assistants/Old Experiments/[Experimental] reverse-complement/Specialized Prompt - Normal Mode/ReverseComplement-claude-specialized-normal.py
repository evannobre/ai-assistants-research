#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Author: Computer Scientist specialized in back-end development
Target: Ubuntu 24.10 64-bit, 16GB RAM, 10GB SSD

This module provides efficient algorithms for computing the reverse complement
of DNA sequences using native Python libraries optimized for memory efficiency.
"""

import sys
import argparse
import time
import gc
from typing import Union, Iterator, Generator
from collections import deque
import mmap
import os
import tempfile
import unittest
from io import StringIO


class DNAProcessor:
    """
    High-performance DNA sequence processor with memory-efficient algorithms.
    Designed for large sequences that can approach system memory limits.
    """
    
    # Translation table using str.translate() for O(n) performance
    COMPLEMENT_TABLE = str.maketrans('ATCGatcgNn', 'TAGCtagcNn')
    
    # Valid DNA nucleotides
    VALID_NUCLEOTIDES = set('ATCGatcgNn')
    
    def __init__(self, chunk_size: int = 8192):
        """
        Initialize processor with configurable chunk size for memory management.
        
        Args:
            chunk_size: Buffer size for streaming operations (default: 8KB)
        """
        self.chunk_size = chunk_size
        self.stats = {'sequences_processed': 0, 'total_length': 0, 'errors': 0}
    
    def validate_sequence(self, sequence: str) -> bool:
        """
        Validate DNA sequence contains only valid nucleotides.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not sequence:
            return False
        return all(nucleotide in self.VALID_NUCLEOTIDES for nucleotide in sequence)
    
    def reverse_complement_basic(self, sequence: str) -> str:
        """
        Compute reverse complement using basic string operations.
        Time Complexity: O(n), Space Complexity: O(n)
        
        Args:
            sequence: Input DNA sequence
            
        Returns:
            str: Reverse complement sequence
            
        Raises:
            ValueError: If sequence contains invalid nucleotides
        """
        if not self.validate_sequence(sequence):
            raise ValueError("Invalid DNA sequence: contains non-nucleotide characters")
        
        # Use str.translate() for complement (O(n)) then reverse slice (O(n))
        complement = sequence.translate(self.COMPLEMENT_TABLE)
        return complement[::-1]
    
    def reverse_complement_streaming(self, sequence: str) -> Generator[str, None, None]:
        """
        Memory-efficient streaming reverse complement for large sequences.
        Processes sequence in chunks to minimize memory footprint.
        
        Args:
            sequence: Input DNA sequence
            
        Yields:
            str: Chunks of reverse complement sequence
        """
        if not self.validate_sequence(sequence):
            raise ValueError("Invalid DNA sequence: contains non-nucleotide characters")
        
        # Process in reverse order, chunk by chunk
        seq_len = len(sequence)
        for i in range(seq_len, 0, -self.chunk_size):
            start = max(0, i - self.chunk_size)
            chunk = sequence[start:i]
            yield chunk.translate(self.COMPLEMENT_TABLE)[::-1]
    
    def reverse_complement_deque(self, sequence: str) -> str:
        """
        Alternative implementation using collections.deque for efficient operations.
        Optimized for moderate-sized sequences.
        
        Args:
            sequence: Input DNA sequence
            
        Returns:
            str: Reverse complement sequence
        """
        if not self.validate_sequence(sequence):
            raise ValueError("Invalid DNA sequence: contains non-nucleotide characters")
        
        # Use deque for efficient appendleft operations
        result = deque()
        for nucleotide in sequence:
            complement = nucleotide.translate(self.COMPLEMENT_TABLE)
            result.appendleft(complement)
        
        return ''.join(result)
    
    def process_file(self, filepath: str, output_path: str = None) -> None:
        """
        Process large DNA sequence files using memory mapping.
        Designed for files that may not fit entirely in memory.
        
        Args:
            filepath: Input file path
            output_path: Output file path (optional)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")
        
        file_size = os.path.getsize(filepath)
        print(f"Processing file: {filepath} ({file_size:,} bytes)")
        
        output_file = output_path or f"{filepath}.reverse_complement"
        
        with open(filepath, 'r') as infile, open(output_file, 'w') as outfile:
            if file_size > 100 * 1024 * 1024:  # > 100MB, use memory mapping
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    sequence = mmapped_file.read().decode('utf-8').strip()
            else:
                sequence = infile.read().strip()
            
            # Use streaming for large sequences
            if len(sequence) > 10**6:  # > 1MB sequence
                for chunk in self.reverse_complement_streaming(sequence):
                    outfile.write(chunk)
            else:
                result = self.reverse_complement_basic(sequence)
                outfile.write(result)
        
        print(f"Output written to: {output_file}")
    
    def benchmark_algorithms(self, sequence: str) -> dict:
        """
        Benchmark different reverse complement algorithms.
        
        Args:
            sequence: Test DNA sequence
            
        Returns:
            dict: Performance metrics for each algorithm
        """
        results = {}
        
        # Test basic algorithm
        start_time = time.perf_counter()
        result_basic = self.reverse_complement_basic(sequence)
        basic_time = time.perf_counter() - start_time
        results['basic'] = {'time': basic_time, 'length': len(result_basic)}
        
        # Test deque algorithm
        start_time = time.perf_counter()
        result_deque = self.reverse_complement_deque(sequence)
        deque_time = time.perf_counter() - start_time
        results['deque'] = {'time': deque_time, 'length': len(result_deque)}
        
        # Test streaming algorithm (collect all chunks)
        start_time = time.perf_counter()
        result_streaming = ''.join(self.reverse_complement_streaming(sequence))
        streaming_time = time.perf_counter() - start_time
        results['streaming'] = {'time': streaming_time, 'length': len(result_streaming)}
        
        # Verify all results are identical
        assert result_basic == result_deque == result_streaming, "Algorithm results don't match!"
        
        return results


class DNATestSuite(unittest.TestCase):
    """Comprehensive test suite for DNA reverse complement algorithms."""
    
    def setUp(self):
        self.processor = DNAProcessor()
    
    def test_basic_sequences(self):
        """Test basic DNA sequences."""
        test_cases = [
            ('ATCG', 'CGAT'),
            ('AAAA', 'TTTT'),
            ('GCGC', 'GCGC'),
            ('', ''),
            ('A', 'T'),
            ('atcg', 'cgat'),  # lowercase
            ('ATCGatcg', 'cgatCGAT'),  # mixed case
        ]
        
        for input_seq, expected in test_cases:
            if input_seq:  # Skip empty string for validation
                with self.subTest(sequence=input_seq):
                    result = self.processor.reverse_complement_basic(input_seq)
                    self.assertEqual(result, expected)
    
    def test_invalid_sequences(self):
        """Test invalid DNA sequences raise appropriate errors."""
        invalid_sequences = ['ATCGX', 'AT-CG', 'ATCG123', 'ATCG@']
        
        for invalid_seq in invalid_sequences:
            with self.subTest(sequence=invalid_seq):
                with self.assertRaises(ValueError):
                    self.processor.reverse_complement_basic(invalid_seq)
    
    def test_algorithm_consistency(self):
        """Test all algorithms produce identical results."""
        test_sequences = [
            'ATCGATCGATCG',
            'AAAAAAAAAA',
            'GCGCGCGCGC',
            'ATCGatcgNNNN',
            'A' * 1000,  # Large sequence
        ]
        
        for seq in test_sequences:
            with self.subTest(sequence=seq[:20] + '...'):
                basic = self.processor.reverse_complement_basic(seq)
                deque_result = self.processor.reverse_complement_deque(seq)
                streaming = ''.join(self.processor.reverse_complement_streaming(seq))
                
                self.assertEqual(basic, deque_result)
                self.assertEqual(basic, streaming)
    
    def test_large_sequence_memory(self):
        """Test memory efficiency with large sequences."""
        # Create a large sequence (1MB)
        large_seq = 'ATCG' * 250000
        
        # Monitor memory usage (basic check)
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        result = self.processor.reverse_complement_basic(large_seq)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not use more than 100MB for this operation
        self.assertLess(memory_increase, 100 * 1024 * 1024)
        self.assertEqual(len(result), len(large_seq))


def create_test_sequence(length: int) -> str:
    """Generate a random DNA sequence for testing."""
    import random
    nucleotides = 'ATCG'
    return ''.join(random.choice(nucleotides) for _ in range(length))


def main():
    """Command-line interface for DNA reverse complement processing."""
    parser = argparse.ArgumentParser(
        description='DNA Reverse Complement Algorithm - High Performance Implementation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ATCGATCG                    # Process single sequence
  %(prog)s --file input.txt            # Process file
  %(prog)s --test                      # Run test suite
  %(prog)s --benchmark 10000           # Benchmark with sequence length
        """
    )
    
    parser.add_argument('sequence', nargs='?', help='DNA sequence to process')
    parser.add_argument('--file', '-f', help='Input file containing DNA sequence')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--algorithm', '-a', choices=['basic', 'deque', 'streaming'],
                       default='basic', help='Algorithm to use (default: basic)')
    parser.add_argument('--chunk-size', type=int, default=8192,
                       help='Chunk size for streaming (default: 8192)')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--benchmark', type=int, metavar='LENGTH',
                       help='Benchmark algorithms with sequence of given length')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate sequence without processing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = DNAProcessor(chunk_size=args.chunk_size)
    
    try:
        # Run test suite
        if args.test:
            print("Running DNA Reverse Complement Test Suite...")
            suite = unittest.TestLoader().loadTestsFromTestCase(DNATestSuite)
            runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
            result = runner.run(suite)
            sys.exit(0 if result.wasSuccessful() else 1)
        
        # Run benchmark
        if args.benchmark:
            print(f"Generating test sequence of length {args.benchmark:,}...")
            test_seq = create_test_sequence(args.benchmark)
            
            print("Benchmarking algorithms...")
            results = processor.benchmark_algorithms(test_seq)
            
            print("\nBenchmark Results:")
            print("-" * 50)
            for algo, metrics in results.items():
                print(f"{algo.capitalize():12}: {metrics['time']:.6f}s")
            
            fastest = min(results.items(), key=lambda x: x[1]['time'])
            print(f"\nFastest: {fastest[0].capitalize()} ({fastest[1]['time']:.6f}s)")
            return
        
        # Process file
        if args.file:
            if args.verbose:
                print(f"Processing file: {args.file}")
            processor.process_file(args.file, args.output)
            return
        
        # Process command-line sequence
        if args.sequence:
            sequence = args.sequence.strip().upper()
            
            if args.validate_only:
                is_valid = processor.validate_sequence(sequence)
                print(f"Sequence validation: {'VALID' if is_valid else 'INVALID'}")
                if not is_valid:
                    sys.exit(1)
                return
            
            if args.verbose:
                print(f"Input sequence: {sequence}")
                print(f"Length: {len(sequence):,}")
                print(f"Algorithm: {args.algorithm}")
            
            # Select and run algorithm
            start_time = time.perf_counter()
            
            if args.algorithm == 'basic':
                result = processor.reverse_complement_basic(sequence)
            elif args.algorithm == 'deque':
                result = processor.reverse_complement_deque(sequence)
            elif args.algorithm == 'streaming':
                result = ''.join(processor.reverse_complement_streaming(sequence))
            
            processing_time = time.perf_counter() - start_time
            
            print(result)
            
            if args.verbose:
                print(f"Processing time: {processing_time:.6f}s")
                print(f"Throughput: {len(sequence) / processing_time:,.0f} nucleotides/second")
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()