#!/usr/bin/env python3
"""
FASTA Simulation using Linear Congruential Generator
Optimized for Ubuntu 24.04.2 LTS with 16GB RAM and 30GB SSD

This implementation uses a naïve LCG for pseudorandom number generation
to simulate DNA/RNA/Protein sequences in FASTA format.
"""

import sys
import os
import gc
import time
from typing import Generator, List, Tuple, Optional
from dataclasses import dataclass
from io import StringIO
import argparse


@dataclass
class LCGParameters:
    """Linear Congruential Generator parameters using well-known constants"""
    # Using Numerical Recipes parameters (widely used, good statistical properties)
    a: int = 1664525      # multiplier
    c: int = 1013904223   # increment  
    m: int = 2**32        # modulus (2^32)
    seed: int = 1         # initial seed


class LinearCongruentialGenerator:
    """
    Naïve Linear Congruential Generator implementation
    Formula: X_{n+1} = (a * X_n + c) mod m
    """
    
    def __init__(self, params: LCGParameters):
        self.params = params
        self.current = params.seed
        self.cycle_count = 0
    
    def next_int(self) -> int:
        """Generate next integer in sequence"""
        self.current = (self.params.a * self.current + self.params.c) % self.params.m
        self.cycle_count += 1
        return self.current
    
    def next_float(self) -> float:
        """Generate next float in range [0, 1)"""
        return self.next_int() / self.params.m
    
    def next_choice(self, choices: List[str]) -> str:
        """Choose random element from list"""
        index = self.next_int() % len(choices)
        return choices[index]
    
    def reset(self, seed: Optional[int] = None):
        """Reset generator with optional new seed"""
        if seed is not None:
            self.params.seed = seed
        self.current = self.params.seed
        self.cycle_count = 0


class FastaSequenceGenerator:
    """Generate biological sequences using LCG"""
    
    # Standard nucleotide and amino acid alphabets
    DNA_BASES = ['A', 'T', 'G', 'C']
    RNA_BASES = ['A', 'U', 'G', 'C']
    AMINO_ACIDS = [
        'A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I',
        'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V'
    ]
    
    def __init__(self, lcg: LinearCongruentialGenerator):
        self.lcg = lcg
    
    def generate_dna_sequence(self, length: int) -> str:
        """Generate random DNA sequence"""
        return ''.join(self.lcg.next_choice(self.DNA_BASES) for _ in range(length))
    
    def generate_rna_sequence(self, length: int) -> str:
        """Generate random RNA sequence"""
        return ''.join(self.lcg.next_choice(self.RNA_BASES) for _ in range(length))
    
    def generate_protein_sequence(self, length: int) -> str:
        """Generate random protein sequence"""
        return ''.join(self.lcg.next_choice(self.AMINO_ACIDS) for _ in range(length))
    
    def generate_weighted_sequence(self, alphabet: List[str], weights: List[float], length: int) -> str:
        """Generate sequence with weighted probability distribution"""
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Create cumulative distribution
        cumulative = []
        cum_sum = 0.0
        for weight in normalized_weights:
            cum_sum += weight
            cumulative.append(cum_sum)
        
        sequence = []
        for _ in range(length):
            rand_val = self.lcg.next_float()
            for i, cum_weight in enumerate(cumulative):
                if rand_val <= cum_weight:
                    sequence.append(alphabet[i])
                    break
        
        return ''.join(sequence)


class FastaSimulator:
    """Main FASTA simulation class with memory optimization"""
    
    def __init__(self, lcg_params: Optional[LCGParameters] = None):
        self.lcg_params = lcg_params or LCGParameters()
        self.lcg = LinearCongruentialGenerator(self.lcg_params)
        self.seq_generator = FastaSequenceGenerator(self.lcg)
        self.memory_threshold = 1024 * 1024 * 1024  # 1GB threshold for garbage collection
    
    def format_fasta_entry(self, header: str, sequence: str, line_width: int = 80) -> str:
        """Format sequence as FASTA entry with specified line width"""
        lines = [f">{header}"]
        for i in range(0, len(sequence), line_width):
            lines.append(sequence[i:i + line_width])
        return '\n'.join(lines) + '\n'
    
    def simulate_batch(self, 
                      seq_type: str,
                      num_sequences: int,
                      min_length: int,
                      max_length: int,
                      prefix: str = "seq") -> Generator[str, None, None]:
        """
        Generate FASTA sequences in batches to manage memory
        
        Args:
            seq_type: 'dna', 'rna', or 'protein'
            num_sequences: Number of sequences to generate
            min_length: Minimum sequence length
            max_length: Maximum sequence length
            prefix: Prefix for sequence headers
        """
        
        sequence_functions = {
            'dna': self.seq_generator.generate_dna_sequence,
            'rna': self.seq_generator.generate_rna_sequence,
            'protein': self.seq_generator.generate_protein_sequence
        }
        
        if seq_type not in sequence_functions:
            raise ValueError(f"Invalid sequence type: {seq_type}")
        
        generate_func = sequence_functions[seq_type]
        
        for i in range(num_sequences):
            # Generate random length within bounds
            length = min_length + (self.lcg.next_int() % (max_length - min_length + 1))
            
            # Generate sequence
            sequence = generate_func(length)
            
            # Create header with metadata
            header = f"{prefix}_{i+1} length={length} type={seq_type} lcg_cycle={self.lcg.cycle_count}"
            
            # Format as FASTA
            fasta_entry = self.format_fasta_entry(header, sequence)
            
            yield fasta_entry
            
            # Periodic garbage collection for memory management
            if (i + 1) % 1000 == 0:
                gc.collect()
    
    def simulate_to_file(self,
                        output_file: str,
                        seq_type: str,
                        num_sequences: int,
                        min_length: int,
                        max_length: int,
                        batch_size: int = 1000) -> None:
        """
        Simulate sequences and write directly to file to minimize memory usage
        """
        
        print(f"Starting FASTA simulation:")
        print(f"  Sequence type: {seq_type}")
        print(f"  Number of sequences: {num_sequences}")
        print(f"  Length range: {min_length}-{max_length}")
        print(f"  Output file: {output_file}")
        print(f"  LCG parameters: a={self.lcg_params.a}, c={self.lcg_params.c}, m={self.lcg_params.m}")
        
        start_time = time.time()
        
        with open(output_file, 'w', buffering=8192) as f:
            batch_count = 0
            for i, fasta_entry in enumerate(self.simulate_batch(seq_type, num_sequences, min_length, max_length)):
                f.write(fasta_entry)
                
                # Progress reporting
                if (i + 1) % batch_size == 0:
                    batch_count += 1
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    print(f"  Processed {i + 1}/{num_sequences} sequences ({rate:.1f} seq/s)")
                    
                    # Memory usage check
                    if hasattr(os, 'getloadavg'):
                        load_avg = os.getloadavg()[0]
                        if load_avg > 2.0:  # High system load
                            time.sleep(0.1)  # Brief pause
        
        elapsed = time.time() - start_time
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"Simulation completed in {elapsed:.2f} seconds")
        print(f"Output file size: {file_size:.2f} MB")
        print(f"Final LCG cycle count: {self.lcg.cycle_count}")
    
    def analyze_sequence_stats(self, sequence: str, seq_type: str) -> dict:
        """Analyze basic statistics of generated sequence"""
        stats = {
            'length': len(sequence),
            'composition': {}
        }
        
        alphabet = {
            'dna': self.seq_generator.DNA_BASES,
            'rna': self.seq_generator.RNA_BASES,
            'protein': self.seq_generator.AMINO_ACIDS
        }.get(seq_type, list(set(sequence)))
        
        for base in alphabet:
            count = sequence.count(base)
            stats['composition'][base] = {
                'count': count,
                'frequency': count / len(sequence) if len(sequence) > 0 else 0
            }
        
        return stats


def main():
    """Command-line interface for FASTA simulation"""
    parser = argparse.ArgumentParser(description='FASTA Simulation using Linear Congruential Generator')
    parser.add_argument('--type', choices=['dna', 'rna', 'protein'], default='dna',
                       help='Type of sequence to generate')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of sequences to generate')
    parser.add_argument('--min-length', type=int, default=100,
                       help='Minimum sequence length')
    parser.add_argument('--max-length', type=int, default=1000,
                       help='Maximum sequence length')
    parser.add_argument('--output', type=str, default='simulation_output.fasta',
                       help='Output FASTA file')
    parser.add_argument('--seed', type=int, default=1,
                       help='LCG seed value')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for progress reporting')
    parser.add_argument('--test', action='store_true',
                       help='Run a small test simulation')
    
    args = parser.parse_args()
    
    # Create LCG parameters with custom seed
    lcg_params = LCGParameters(seed=args.seed)
    
    # Initialize simulator
    simulator = FastaSimulator(lcg_params)
    
    if args.test:
        # Run small test
        print("Running test simulation...")
        simulator.simulate_to_file(
            output_file='test_output.fasta',
            seq_type=args.type,
            num_sequences=10,
            min_length=50,
            max_length=200,
            batch_size=5
        )
        
        # Analyze first sequence
        with open('test_output.fasta', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                sequence = ''.join(line.strip() for line in lines[1:] if not line.startswith('>'))
                stats = simulator.analyze_sequence_stats(sequence, args.type)
                print(f"\nFirst sequence statistics:")
                print(f"  Length: {stats['length']}")
                print(f"  Composition: {stats['composition']}")
    else:
        # Run full simulation
        simulator.simulate_to_file(
            output_file=args.output,
            seq_type=args.type,
            num_sequences=args.count,
            min_length=args.min_length,
            max_length=args.max_length,
            batch_size=args.batch_size
        )


if __name__ == "__main__":
    main()