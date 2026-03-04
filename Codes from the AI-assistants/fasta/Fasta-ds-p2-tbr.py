#!/usr/bin/env python3
"""
FASTA Simulation with Naïve Linear Congruential Generator
Author: Back-End Specialist
System: Ubuntu 24.04.4 64-bit (256 GB SSD, 8 GB RAM)
"""

import sys
import os
import time
import argparse
import math
import gzip
import hashlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Iterator, Optional
from datetime import datetime

@dataclass
class SystemConstraints:
    """Enforce system resource constraints"""
    MAX_MEMORY_MB: int = 6000  # Leave 2GB for OS
    MAX_SEQUENCES: int = 1000000
    MAX_SEQUENCE_LENGTH: int = 1000000
    CHUNK_SIZE: int = 100000  # Process in chunks to save memory
    
    @classmethod
    def check_memory_usage(cls, estimated_mb: float) -> bool:
        """Check if estimated memory usage is within limits"""
        if estimated_mb > cls.MAX_MEMORY_MB:
            raise MemoryError(
                f"Estimated memory usage ({estimated_mb:.1f} MB) exceeds "
                f"limit ({cls.MAX_MEMORY_MB} MB)"
            )
        return True

class NaiveLCG:
    """
    Naïve Linear Congruential Generator for DNA sequence simulation
    X_{n+1} = (a * X_n + c) mod m
    """
    
    # Parameters from "Numerical Recipes" (not cryptographically secure!)
    DEFAULT_A = 1664525
    DEFAULT_C = 1013904223
    DEFAULT_M = 2**32
    
    # DNA nucleotide mapping
    NUCLEOTIDES = ['A', 'C', 'G', 'T']
    COMPLEMENT = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    
    def __init__(self, seed: int = None, 
                 a: int = DEFAULT_A, 
                 c: int = DEFAULT_C, 
                 m: int = DEFAULT_M):
        """
        Initialize LCG with parameters
        
        Args:
            seed: Initial seed value
            a: Multiplier
            c: Increment
            m: Modulus
        """
        self.a = a
        self.c = c
        self.m = m
        self.state = seed if seed is not None else int(time.time() * 1000) % m
        self.original_seed = self.state
        
    def next(self) -> int:
        """Generate next random number"""
        self.state = (self.a * self.state + self.c) % self.m
        return self.state
    
    def random_float(self) -> float:
        """Generate random float in [0, 1)"""
        return self.next() / self.m
    
    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate random integer in [min_val, max_val]"""
        return min_val + (self.next() % (max_val - min_val + 1))
    
    def random_nucleotide(self) -> str:
        """Generate random nucleotide (A, C, G, T)"""
        idx = self.next() % 4
        return self.NUCLEOTIDES[idx]
    
    def generate_dna_sequence(self, length: int) -> str:
        """Generate random DNA sequence of specified length"""
        return ''.join(self.random_nucleotide() for _ in range(length))
    
    def generate_sequence_with_gc_content(self, length: int, gc_target: float = 0.5) -> str:
        """Generate DNA sequence with specific GC content"""
        sequence = []
        for _ in range(length):
            if self.random_float() < gc_target:
                # Choose between G or C
                sequence.append('G' if self.random_float() < 0.5 else 'C')
            else:
                # Choose between A or T
                sequence.append('A' if self.random_float() < 0.5 else 'T')
        return ''.join(sequence)
    
    def reset(self) -> None:
        """Reset generator to original seed"""
        self.state = self.original_seed

class FASTASimulator:
    """FASTA format sequence simulator using LCG"""
    
    def __init__(self, seed: int = None, compression: bool = False):
        self.lcg = NaiveLCG(seed)
        self.compression = compression
        self.stats = defaultdict(int)
        
    def generate_fasta_header(self, seq_id: int, 
                            description: str = None) -> str:
        """Generate FASTA header line"""
        if description is None:
            description = f"simulated sequence {seq_id}"
        return f">seq_{seq_id:06d} {description}"
    
    def estimate_memory_usage(self, num_sequences: int, 
                            avg_length: int) -> float:
        """
        Estimate memory usage in MB
        Each character ~1 byte + Python overhead (~49 bytes per string)
        """
        sequence_memory = num_sequences * avg_length
        overhead_memory = num_sequences * 49  # Python string overhead
        total_bytes = sequence_memory + overhead_memory
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def validate_parameters(self, num_sequences: int, 
                          min_length: int, max_length: int) -> None:
        """Validate simulation parameters"""
        constraints = SystemConstraints()
        
        if num_sequences <= 0 or num_sequences > constraints.MAX_SEQUENCES:
            raise ValueError(
                f"Number of sequences must be between 1 and {constraints.MAX_SEQUENCES}"
            )
        
        if min_length <= 0 or max_length <= 0:
            raise ValueError("Sequence length must be positive")
        
        if min_length > max_length:
            raise ValueError("Minimum length cannot exceed maximum length")
        
        if max_length > constraints.MAX_SEQUENCE_LENGTH:
            raise ValueError(
                f"Maximum sequence length cannot exceed {constraints.MAX_SEQUENCE_LENGTH}"
            )
        
        # Estimate and check memory usage
        avg_length = (min_length + max_length) // 2
        estimated_memory = self.estimate_memory_usage(num_sequences, avg_length)
        constraints.check_memory_usage(estimated_memory)
        
    def generate_sequences_chunked(self, num_sequences: int,
                                 min_length: int, max_length: int,
                                 gc_content: float = 0.5) -> Iterator[Tuple[str, str]]:
        """
        Generate sequences in chunks to conserve memory
        
        Yields:
            Tuple of (header, sequence)
        """
        constraints = SystemConstraints()
        chunk_size = min(constraints.CHUNK_SIZE, num_sequences)
        
        for chunk_start in range(0, num_sequences, chunk_size):
            chunk_end = min(chunk_start + chunk_size, num_sequences)
            
            for seq_id in range(chunk_start, chunk_end):
                # Generate random length for this sequence
                length = self.lcg.random_int(min_length, max_length)
                
                # Generate sequence with specified GC content
                if gc_content is not None:
                    sequence = self.lcg.generate_sequence_with_gc_content(
                        length, gc_content
                    )
                else:
                    sequence = self.lcg.generate_dna_sequence(length)
                
                # Generate header
                header = self.generate_fasta_header(
                    seq_id,
                    f"len={length} gc={self.calculate_gc_content(sequence):.3f}"
                )
                
                # Update statistics
                self.stats['total_sequences'] += 1
                self.stats['total_bases'] += length
                self.stats['min_length'] = min(
                    self.stats.get('min_length', length), length
                )
                self.stats['max_length'] = max(
                    self.stats.get('max_length', 0), length
                )
                
                yield header, sequence
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content of a DNA sequence"""
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0.0
    
    def simulate(self, output_file: str, num_sequences: int,
                min_length: int, max_length: int,
                gc_content: float = 0.5) -> dict:
        """
        Main simulation method
        
        Returns:
            Dictionary with simulation statistics
        """
        print(f"Starting FASTA simulation...")
        print(f"Parameters: {num_sequences} sequences, "
              f"length {min_length}-{max_length}, "
              f"GC content: {gc_content}")
        
        # Validate parameters
        self.validate_parameters(num_sequences, min_length, max_length)
        
        # Generate sequences and write to file
        start_time = time.time()
        
        if self.compression:
            output_file = output_file + '.gz'
        
        try:
            with gzip.open(output_file, 'wt', encoding='utf-8') if self.compression \
                 else open(output_file, 'w', encoding='utf-8') as f:
                
                sequences_generated = 0
                
                for header, sequence in self.generate_sequences_chunked(
                    num_sequences, min_length, max_length, gc_content
                ):
                    # Write FASTA format
                    f.write(f"{header}\n")
                    
                    # Write sequence in lines of 80 characters (FASTA standard)
                    for i in range(0, len(sequence), 80):
                        f.write(f"{sequence[i:i+80]}\n")
                    
                    sequences_generated += 1
                    
                    # Progress indicator
                    if sequences_generated % 1000 == 0:
                        elapsed = time.time() - start_time
                        print(f"  Generated {sequences_generated}/{num_sequences} sequences "
                              f"({elapsed:.1f}s)")
        
        except IOError as e:
            print(f"Error writing to file: {e}")
            raise
        
        # Calculate final statistics
        elapsed_time = time.time() - start_time
        
        # Calculate file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        # Update stats
        self.stats['elapsed_time'] = elapsed_time
        self.stats['file_size_mb'] = file_size_mb
        self.stats['sequences_per_second'] = num_sequences / elapsed_time
        self.stats['bases_per_second'] = self.stats['total_bases'] / elapsed_time
        
        if self.stats['total_sequences'] > 0:
            self.stats['avg_length'] = (
                self.stats['total_bases'] / self.stats['total_sequences']
            )
        
        return dict(self.stats)

def analyze_fasta_file(filename: str) -> dict:
    """Analyze generated FASTA file"""
    analysis = defaultdict(int)
    
    try:
        # Try gzipped first
        try:
            f = gzip.open(filename, 'rt', encoding='utf-8')
        except (gzip.BadGzipFile, OSError):
            f = open(filename, 'r', encoding='utf-8')
        
        with f:
            current_seq = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('>'):
                    # Finish previous sequence
                    if current_seq:
                        seq = ''.join(current_seq)
                        analysis['gc_content'] += (
                            seq.count('G') + seq.count('C')
                        ) / len(seq)
                        current_seq = []
                    analysis['sequences'] += 1
                else:
                    current_seq.append(line)
                    analysis['total_length'] += len(line)
            
            # Process last sequence
            if current_seq:
                seq = ''.join(current_seq)
                analysis['gc_content'] += (
                    seq.count('G') + seq.count('C')
                ) / len(seq)
        
        if analysis['sequences'] > 0:
            analysis['avg_gc_content'] = (
                analysis['gc_content'] / analysis['sequences']
            )
            analysis['avg_length'] = (
                analysis['total_length'] / analysis['sequences']
            )
    
    except FileNotFoundError:
        print(f"File {filename} not found")
    
    return dict(analysis)

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='FASTA Simulation with Naïve Linear Congruential Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('-o', '--output', default='simulated.fasta',
                       help='Output FASTA filename')
    parser.add_argument('-n', '--num-sequences', type=int, default=1000,
                       help='Number of sequences to generate')
    parser.add_argument('--min-length', type=int, default=100,
                       help='Minimum sequence length')
    parser.add_argument('--max-length', type=int, default=1000,
                       help='Maximum sequence length')
    parser.add_argument('--gc-content', type=float, default=0.5,
                       help='Target GC content (0.0 to 1.0)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    parser.add_argument('--compress', action='store_true',
                       help='Compress output with gzip')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze generated file')
    
    args = parser.parse_args()
    
    # Validate GC content
    if not 0.0 <= args.gc_content <= 1.0:
        print("Error: GC content must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Create simulator
    simulator = FASTASimulator(seed=args.seed, compression=args.compress)
    
    try:
        # Run simulation
        stats = simulator.simulate(
            output_file=args.output,
            num_sequences=args.num_sequences,
            min_length=args.min_length,
            max_length=args.max_length,
            gc_content=args.gc_content
        )
        
        # Print statistics
        print("\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        print(f"Output file: {args.output}{'.gz' if args.compress else ''}")
        print(f"Sequences generated: {stats['total_sequences']:,}")
        print(f"Total bases: {stats['total_bases']:,}")
        print(f"Length range: {stats['min_length']:,} - {stats['max_length']:,}")
        print(f"Average length: {stats.get('avg_length', 0):,.1f}")
        print(f"File size: {stats['file_size_mb']:.2f} MB")
        print(f"Time elapsed: {stats['elapsed_time']:.2f} seconds")
        print(f"Sequences/second: {stats['sequences_per_second']:.1f}")
        print(f"Bases/second: {stats['bases_per_second']:,.0f}")
        print(f"Memory safe: Yes (estimated < {SystemConstraints.MAX_MEMORY_MB} MB)")
        
        # Analyze file if requested
        if args.analyze:
            print("\n" + "="*60)
            print("FILE ANALYSIS")
            print("="*60)
            filename = args.output + ('.gz' if args.compress else '')
            analysis = analyze_fasta_file(filename)
            
            if analysis:
                print(f"Sequences in file: {analysis['sequences']:,}")
                print(f"Total length: {analysis['total_length']:,}")
                print(f"Average length: {analysis.get('avg_length', 0):.1f}")
                print(f"Average GC content: {analysis.get('avg_gc_content', 0):.3f}")
                print(f"Target GC content: {args.gc_content:.3f}")
        
        print("\nSystem resources respected:")
        print(f"  - RAM limit: {SystemConstraints.MAX_MEMORY_MB} MB")
        print(f"  - Chunked processing: {SystemConstraints.CHUNK_SIZE} sequences/chunk")
        print(f"  - Disk-friendly: Sequential writes, optional compression")
        
    except (ValueError, MemoryError) as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()