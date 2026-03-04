#!/usr/bin/env python3
"""
FASTA Simulation with Linear Congruential Generator (LCG)
Optimized for Ubuntu 24.04.4 64-bit with 8GB RAM and 256GB SSD
Uses native Python libraries only
"""

import sys
import os
import time
import argparse
from typing import Generator, Tuple
from pathlib import Path
import gzip
import math

class LCG:
    """Naïve Linear Congruential Generator for DNA sequence simulation"""
    
    def __init__(self, seed: int = None):
        """
        Initialize LCG with parameters for good statistical properties
        Using parameters from Numerical Recipes: a=1664525, c=1013904223, m=2^32
        """
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32
        
        # Use system time if no seed provided
        self.state = seed if seed is not None else int(time.time() * 1000) % self.m
        
    def next_int(self) -> int:
        """Generate next random integer"""
        self.state = (self.a * self.state + self.c) % self.m
        return self.state
    
    def random(self) -> float:
        """Generate random float in [0, 1)"""
        return self.next_int() / self.m
    
    def choice(self, items: list):
        """Random choice from list using LCG"""
        idx = int(self.random() * len(items))
        return items[idx]

class FASTASimulator:
    """FASTA format simulator with memory-efficient generation"""
    
    # DNA nucleotide frequencies (approximate human genome)
    NUCLEOTIDES = ['A', 'C', 'G', 'T']
    
    # Weighted distribution for more realistic sequences
    WEIGHTED_NUCLEOTIDES = ['A'] * 30 + ['C'] * 20 + ['G'] * 20 + ['T'] * 30
    
    # Common FASTA header prefixes
    HEADER_PREFIXES = ['chr', 'scaffold', 'contig', 'read']
    
    def __init__(self, seed: int = None, use_weighted: bool = True):
        """
        Initialize FASTA simulator
        
        Args:
            seed: Random seed for reproducibility
            use_weighted: Use weighted nucleotide distribution for realism
        """
        self.lcg = LCG(seed)
        self.use_weighted = use_weighted
        self.nucleotides = self.WEIGHTED_NUCLEOTIDES if use_weighted else self.NUCLEOTIDES
        
    def generate_sequence(self, length: int) -> Generator[str, None, None]:
        """
        Generate DNA sequence using LCG in chunks to save memory
        
        Args:
            length: Total sequence length
            
        Yields:
            Sequence chunks as strings
        """
        # Buffer size optimized for 8GB RAM (adjustable)
        buffer_size = min(length, 10_000_000)  # 10MB chunks
        
        for start in range(0, length, buffer_size):
            end = min(start + buffer_size, length)
            chunk_size = end - start
            
            # Generate chunk using list comprehension for speed
            chunk = ''.join(
                self.lcg.choice(self.nucleotides) 
                for _ in range(chunk_size)
            )
            yield chunk
    
    def generate_header(self, seq_id: int, length: int) -> str:
        """Generate realistic FASTA header"""
        prefix = self.lcg.choice(self.HEADER_PREFIXES)
        desc_options = [
            f"simulated sequence {seq_id}",
            f"random DNA LCG generated",
            f"artificial chromosome {seq_id}",
            f"synthetic genomic fragment"
        ]
        desc = self.lcg.choice(desc_options)
        return f">{prefix}_{seq_id} length={length} desc={desc} seed={self.lcg.state}"
    
    def simulate_fasta(
        self,
        num_sequences: int,
        min_length: int,
        max_length: int,
        output_path: str,
        compress: bool = False
    ) -> Tuple[int, float]:
        """
        Generate FASTA file with multiple sequences
        
        Args:
            num_sequences: Number of sequences to generate
            min_length: Minimum sequence length
            max_length: Maximum sequence length
            output_path: Output file path
            compress: Gzip compress output
            
        Returns:
            Tuple of (total_bases, execution_time)
        """
        start_time = time.time()
        total_bases = 0
        
        # Open output file (compressed or regular)
        if compress:
            out_file = gzip.open(output_path, 'wt', encoding='utf-8')
        else:
            out_file = open(output_path, 'w', encoding='utf-8')
        
        try:
            with out_file:
                for seq_id in range(1, num_sequences + 1):
                    # Generate random length for this sequence
                    seq_length = min_length + int(self.lcg.random() * (max_length - min_length))
                    
                    # Write header
                    header = self.generate_header(seq_id, seq_length)
                    out_file.write(header + '\n')
                    
                    # Write sequence in chunks
                    line_length = 80  # Standard FASTA line length
                    bases_written = 0
                    
                    for chunk in self.generate_sequence(seq_length):
                        # Write chunk in FASTA format lines
                        for i in range(0, len(chunk), line_length):
                            line = chunk[i:i + line_length]
                            out_file.write(line + '\n')
                            bases_written += len(line)
                    
                    total_bases += bases_written
                    
                    # Progress indicator for large files
                    if seq_id % 100 == 0:
                        elapsed = time.time() - start_time
                        sys.stderr.write(
                            f"\rGenerated {seq_id}/{num_sequences} sequences "
                            f"({total_bases:,} bases, {elapsed:.1f}s)"
                        )
                        sys.stderr.flush()
        
        except KeyboardInterrupt:
            sys.stderr.write("\n\nSimulation interrupted by user\n")
        except Exception as e:
            sys.stderr.write(f"\n\nError: {e}\n")
            raise
        
        elapsed_time = time.time() - start_time
        return total_bases, elapsed_time

def validate_memory_usage(num_sequences: int, max_length: int) -> bool:
    """
    Validate that simulation won't exceed available memory
    
    Args:
        num_sequences: Number of sequences
        max_length: Maximum sequence length
        
    Returns:
        True if memory usage is acceptable
    """
    # Conservative estimate: 2 bytes per character in memory
    max_memory_estimate = num_sequences * max_length * 2
    
    # Convert to MB
    max_memory_mb = max_memory_estimate / (1024 * 1024)
    
    # Leave 2GB for system (8GB total)
    safe_limit = 6 * 1024  # 6GB in MB
    
    if max_memory_mb > safe_limit:
        sys.stderr.write(
            f"Warning: Estimated memory usage {max_memory_mb:.0f}MB "
            f"exceeds safe limit {safe_limit}MB\n"
        )
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='FASTA Simulation using Linear Congruential Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100 sequences, 1000-5000 bases each
  %(prog)s -n 100 -l 1000 -L 5000 -o simulated.fasta
  
  # Generate large dataset with compression
  %(prog)s -n 10000 -l 10000 -L 100000 -o simulated.fasta.gz --compress
  
  # Reproducible simulation with seed
  %(prog)s -n 50 -l 500 -L 2000 -o test.fasta --seed 42
  
Memory Management:
  The script uses chunked generation to minimize memory usage.
  Maximum recommended settings for 8GB RAM:
    - Up to 1,000,000 sequences with average length 10,000
    - Or 10,000 sequences with average length 100,000
        """
    )
    
    parser.add_argument('-n', '--num-sequences', type=int, default=100,
                       help='Number of sequences to generate (default: 100)')
    parser.add_argument('-l', '--min-length', type=int, default=1000,
                       help='Minimum sequence length (default: 1000)')
    parser.add_argument('-L', '--max-length', type=int, default=5000,
                       help='Maximum sequence length (default: 5000)')
    parser.add_argument('-o', '--output', type=str, default='simulated.fasta',
                       help='Output file path (default: simulated.fasta)')
    parser.add_argument('-s', '--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    parser.add_argument('-c', '--compress', action='store_true',
                       help='Compress output with gzip')
    parser.add_argument('-w', '--weighted', action='store_true',
                       help='Use weighted nucleotide distribution')
    parser.add_argument('--no-validation', action='store_true',
                       help='Skip memory validation (use with caution)')
    
    args = parser.parse_args()
    
    # Input validation
    if args.min_length <= 0 or args.max_length <= 0:
        sys.stderr.write("Error: Sequence lengths must be positive\n")
        sys.exit(1)
    
    if args.min_length > args.max_length:
        sys.stderr.write("Error: min-length must be <= max-length\n")
        sys.exit(1)
    
    if args.num_sequences <= 0:
        sys.stderr.write("Error: Number of sequences must be positive\n")
        sys.exit(1)
    
    # Memory validation
    if not args.no_validation:
        if not validate_memory_usage(args.num_sequences, args.max_length):
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # Check disk space (conservative estimate)
    output_path = Path(args.output)
    estimated_size = args.num_sequences * ((args.min_length + args.max_length) / 2) * 1.1
    estimated_size_gb = estimated_size / (1024**3)
    
    if estimated_size_gb > 200:  # Leave 50GB free on 256GB SSD
        sys.stderr.write(f"Warning: Estimated size {estimated_size_gb:.1f}GB > 200GB\n")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Run simulation
    simulator = FASTASimulator(seed=args.seed, use_weighted=args.weighted)
    
    sys.stderr.write(f"Starting FASTA simulation with LCG\n")
    sys.stderr.write(f"  Sequences: {args.num_sequences:,}\n")
    sys.stderr.write(f"  Length range: {args.min_length:,}-{args.max_length:,}\n")
    sys.stderr.write(f"  Output: {args.output}\n")
    sys.stderr.write(f"  Compression: {'Yes' if args.compress else 'No'}\n")
    sys.stderr.write(f"  Seed: {args.seed if args.seed else 'random'}\n")
    sys.stderr.write("-" * 50 + "\n")
    
    try:
        total_bases, elapsed_time = simulator.simulate_fasta(
            num_sequences=args.num_sequences,
            min_length=args.min_length,
            max_length=args.max_length,
            output_path=args.output,
            compress=args.compress
        )
        
        # Performance statistics
        sys.stderr.write(f"\n\nSimulation complete!\n")
        sys.stderr.write(f"Total sequences: {args.num_sequences:,}\n")
        sys.stderr.write(f"Total bases: {total_bases:,}\n")
        sys.stderr.write(f"Execution time: {elapsed_time:.2f} seconds\n")
        sys.stderr.write(f"Bases per second: {total_bases/elapsed_time:,.0f}\n")
        
        # File size info
        if output_path.exists():
            size_bytes = output_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            sys.stderr.write(f"Output size: {size_mb:.2f} MB\n")
        
    except Exception as e:
        sys.stderr.write(f"Simulation failed: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()