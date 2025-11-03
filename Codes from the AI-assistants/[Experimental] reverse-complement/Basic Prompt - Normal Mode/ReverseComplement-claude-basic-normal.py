#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
================================

This script provides multiple implementations for calculating the reverse complement
of DNA sequences, utilizing Python's native libraries and optimized approaches.
"""

import argparse
import sys
import time
from collections import defaultdict
import re


class DNAProcessor:
    """DNA sequence processor with multiple reverse complement implementations."""
    
    # Standard DNA base pairing rules
    COMPLEMENT_MAP = str.maketrans('ATCG', 'TAGC')
    COMPLEMENT_MAP_EXTENDED = str.maketrans('ATCGRYSWKMBDHVN', 'TAGCYRSW	MKHDBVN')
    
    def __init__(self):
        """Initialize with validation patterns."""
        self.valid_dna_pattern = re.compile(r'^[ATCGRYSWKMBDHVN]+$', re.IGNORECASE)
        self.stats = defaultdict(int)
    
    def validate_sequence(self, sequence):
        """
        Validate DNA sequence using regex.
        
        Args:
            sequence (str): DNA sequence to validate
            
        Returns:
            bool: True if valid DNA sequence
        """
        return bool(self.valid_dna_pattern.match(sequence.strip()))
    
    def reverse_complement_basic(self, sequence):
        """
        Basic reverse complement using string methods.
        
        Args:
            sequence (str): DNA sequence
            
        Returns:
            str: Reverse complement sequence
        """
        sequence = sequence.upper().strip()
        
        # Using translate() method with translation table
        complement = sequence.translate(self.COMPLEMENT_MAP)
        
        # Reverse using slicing
        return complement[::-1]
    
    def reverse_complement_extended(self, sequence):
        """
        Extended reverse complement supporting IUPAC ambiguous bases.
        
        Args:
            sequence (str): DNA sequence with possible ambiguous bases
            
        Returns:
            str: Reverse complement sequence
        """
        sequence = sequence.upper().strip()
        
        # Extended complement map for ambiguous nucleotides
        complement = sequence.translate(self.COMPLEMENT_MAP_EXTENDED)
        
        return complement[::-1]
    
    def reverse_complement_generator(self, sequence):
        """
        Memory-efficient reverse complement using generator.
        
        Args:
            sequence (str): DNA sequence
            
        Returns:
            str: Reverse complement sequence
        """
        sequence = sequence.upper().strip()
        
        complement_dict = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        
        # Generator expression for memory efficiency
        return ''.join(complement_dict.get(base, 'N') for base in reversed(sequence))
    
    def reverse_complement_bytearray(self, sequence):
        """
        High-performance reverse complement using bytearray.
        
        Args:
            sequence (str): DNA sequence
            
        Returns:
            str: Reverse complement sequence
        """
        sequence = sequence.upper().strip()
        
        # Convert to bytearray for in-place operations
        seq_bytes = bytearray(sequence.encode())
        
        # In-place complement
        for i in range(len(seq_bytes)):
            if seq_bytes[i] == ord('A'):
                seq_bytes[i] = ord('T')
            elif seq_bytes[i] == ord('T'):
                seq_bytes[i] = ord('A')
            elif seq_bytes[i] == ord('C'):
                seq_bytes[i] = ord('G')
            elif seq_bytes[i] == ord('G'):
                seq_bytes[i] = ord('C')
        
        # Reverse and convert back to string
        seq_bytes.reverse()
        return seq_bytes.decode()
    
    def analyze_sequence(self, sequence):
        """
        Analyze DNA sequence composition.
        
        Args:
            sequence (str): DNA sequence
            
        Returns:
            dict: Sequence statistics
        """
        sequence = sequence.upper().strip()
        
        stats = {
            'length': len(sequence),
            'A': sequence.count('A'),
            'T': sequence.count('T'),
            'C': sequence.count('C'),
            'G': sequence.count('G'),
        }
        
        stats['GC_content'] = (stats['C'] + stats['G']) / stats['length'] * 100 if stats['length'] > 0 else 0
        stats['AT_content'] = (stats['A'] + stats['T']) / stats['length'] * 100 if stats['length'] > 0 else 0
        
        return stats
    
    def benchmark_methods(self, sequence, iterations=1000):
        """
        Benchmark different reverse complement methods.
        
        Args:
            sequence (str): Test DNA sequence
            iterations (int): Number of iterations for timing
            
        Returns:
            dict: Timing results
        """
        methods = {
            'basic': self.reverse_complement_basic,
            'extended': self.reverse_complement_extended,
            'generator': self.reverse_complement_generator,
            'bytearray': self.reverse_complement_bytearray
        }
        
        results = {}
        
        for name, method in methods.items():
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                method(sequence)
            
            end_time = time.perf_counter()
            results[name] = (end_time - start_time) / iterations * 1000  # ms per operation
        
        return results


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='DNA Reverse Complement Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python dna_reverse_complement.py ATCG
  python dna_reverse_complement.py ATCGATCG --method extended --analyze
  python dna_reverse_complement.py AAATTTCCCGGG --benchmark
  echo "ATCGATCG" | python dna_reverse_complement.py --stdin
        '''
    )
    
    parser.add_argument(
        'sequence', 
        nargs='?', 
        help='DNA sequence to process'
    )
    
    parser.add_argument(
        '--method', 
        choices=['basic', 'extended', 'generator', 'bytearray'],
        default='basic',
        help='Reverse complement method to use (default: basic)'
    )
    
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='Show sequence analysis'
    )
    
    parser.add_argument(
        '--benchmark', 
        action='store_true',
        help='Benchmark all methods'
    )
    
    parser.add_argument(
        '--stdin', 
        action='store_true',
        help='Read sequence from stdin'
    )
    
    parser.add_argument(
        '--validate-only', 
        action='store_true',
        help='Only validate the sequence without processing'
    )
    
    args = parser.parse_args()
    
    # Get sequence from appropriate source
    if args.stdin:
        try:
            sequence = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(1)
    elif args.sequence:
        sequence = args.sequence
    else:
        parser.print_help()
        sys.exit(1)
    
    # Initialize processor
    processor = DNAProcessor()
    
    # Validate sequence
    if not processor.validate_sequence(sequence):
        print(f"Error: Invalid DNA sequence: {sequence}", file=sys.stderr)
        print("Valid characters: A, T, C, G (and IUPAC ambiguous codes for extended method)", file=sys.stderr)
        sys.exit(1)
    
    print(f"Input sequence: {sequence}")
    
    if args.validate_only:
        print("✓ Sequence is valid")
        sys.exit(0)
    
    # Choose method
    method_map = {
        'basic': processor.reverse_complement_basic,
        'extended': processor.reverse_complement_extended,
        'generator': processor.reverse_complement_generator,
        'bytearray': processor.reverse_complement_bytearray
    }
    
    # Calculate reverse complement
    reverse_comp = method_map[args.method](sequence)
    print(f"Reverse complement: {reverse_comp}")
    
    # Analysis
    if args.analyze:
        stats = processor.analyze_sequence(sequence)
        print("\nSequence Analysis:")
        print(f"  Length: {stats['length']} bp")
        print(f"  A: {stats['A']} ({stats['A']/stats['length']*100:.1f}%)")
        print(f"  T: {stats['T']} ({stats['T']/stats['length']*100:.1f}%)")
        print(f"  C: {stats['C']} ({stats['C']/stats['length']*100:.1f}%)")
        print(f"  G: {stats['G']} ({stats['G']/stats['length']*100:.1f}%)")
        print(f"  GC Content: {stats['GC_content']:.1f}%")
        print(f"  AT Content: {stats['AT_content']:.1f}%")
    
    # Benchmark
    if args.benchmark:
        print("\nBenchmarking methods...")
        timing_results = processor.benchmark_methods(sequence)
        print("Performance (average time per operation):")
        for method, time_ms in sorted(timing_results.items(), key=lambda x: x[1]):
            print(f"  {method:10}: {time_ms:.4f} ms")


if __name__ == '__main__':
    main()