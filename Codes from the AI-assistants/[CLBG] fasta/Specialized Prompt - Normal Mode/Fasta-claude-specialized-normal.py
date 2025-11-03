#!/usr/bin/env python3
"""
FASTA simulation using naïve Linear Congruential Generator
Implements sequential algorithm for DNA sequence generation
"""

import sys
import array
from typing import List, Tuple

# Naïve Linear Congruential Generator constants
IM = 139968
IA = 3877
IC = 29573

class NaiveLCG:
    """Naïve Linear Congruential Generator implementation"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def random(self, max_val: float) -> float:
        """Generate next random number using LCG formula"""
        self.seed = (self.seed * IA + IC) % IM
        return max_val * self.seed / IM

class FastaSimulator:
    """FASTA sequence simulator using naïve LCG"""
    
    def __init__(self):
        self.lcg = NaiveLCG(42)  # Initialize with seed = 42
        
        # Homosapiens frequency data
        self.homo_sapiens = [
            ('a', 0.3029549426680),
            ('c', 0.1979883004921),
            ('g', 0.1975473066391),
            ('t', 0.3015094502008)
        ]
        
        # IUB ambiguity codes
        self.iub = [
            ('a', 0.27),
            ('c', 0.12),
            ('g', 0.12),
            ('t', 0.27),
            ('B', 0.02),
            ('D', 0.02),
            ('H', 0.02),
            ('K', 0.02),
            ('M', 0.02),
            ('N', 0.02),
            ('R', 0.02),
            ('S', 0.02),
            ('V', 0.02),
            ('W', 0.02),
            ('Y', 0.02)
        ]
        
        # ALU sequence for repeating
        self.alu = (
            "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
            "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
            "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
            "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
            "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
            "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
            "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
        )
    
    def make_cumulative_table(self, frequencies: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Convert probabilities to cumulative probabilities"""
        cumulative = []
        total = 0.0
        
        for nucleotide, prob in frequencies:
            total += prob
            cumulative.append((nucleotide, total))
        
        return cumulative
    
    def select_nucleotide(self, cumulative_table: List[Tuple[str, float]]) -> str:
        """Select nucleotide using linear search against cumulative probabilities"""
        random_val = self.lcg.random(1.0)
        
        # Linear search through cumulative probabilities
        for nucleotide, cum_prob in cumulative_table:
            if random_val < cum_prob:
                return nucleotide
        
        # Fallback (should not happen with proper probabilities)
        return cumulative_table[-1][0]
    
    def generate_repeating_sequence(self, sequence: str, length: int, description: str):
        """Generate DNA sequence by copying from given sequence"""
        print(f">{description}")
        
        seq_len = len(sequence)
        line_length = 60
        generated = 0
        
        while generated < length:
            line_start = generated
            line_end = min(generated + line_length, length)
            line_chars = line_end - line_start
            
            # Build line character by character
            line = []
            for i in range(line_chars):
                pos = (line_start + i) % seq_len
                line.append(sequence[pos])
            
            print(''.join(line))
            generated = line_end
    
    def generate_random_sequence(self, frequencies: List[Tuple[str, float]], 
                                length: int, description: str):
        """Generate DNA sequence by weighted random selection"""
        print(f">{description}")
        
        cumulative_table = self.make_cumulative_table(frequencies)
        line_length = 60
        generated = 0
        
        while generated < length:
            line_start = generated
            line_end = min(generated + line_length, length)
            line_chars = line_end - line_start
            
            # Build line character by character using LCG
            line = []
            for _ in range(line_chars):
                nucleotide = self.select_nucleotide(cumulative_table)
                line.append(nucleotide)
            
            print(''.join(line))
            generated = line_end
    
    def run_simulation(self, n: int):
        """Run complete FASTA simulation"""
        # Generate THREE Homo sapiens frequency sequence
        self.generate_random_sequence(
            self.homo_sapiens, 
            n * 2, 
            "THREE Homo sapiens frequency"
        )
        
        # Generate TWO IUB ambiguity sequence  
        self.generate_random_sequence(
            self.iub, 
            n * 3, 
            "TWO IUB ambiguity codes"
        )
        
        # Generate ONE Homo sapiens ALU repeating sequence
        self.generate_repeating_sequence(
            self.alu, 
            n * 5, 
            "ONE Homo sapiens alu"
        )

def main():
    """Main function to handle command line arguments and run simulation"""
    if len(sys.argv) != 2:
        print("Usage: python3 fasta.py <n>", file=sys.stderr)
        print("Example: python3 fasta.py 25000000", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError("N must be positive")
    except ValueError as e:
        print(f"Error: Invalid argument. {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check memory constraints for large inputs
    if n > 10000000:  # ~10M threshold for memory safety
        print(f"Warning: Large input size {n}. Processing...", file=sys.stderr)
    
    simulator = FastaSimulator()
    simulator.run_simulation(n)

if __name__ == "__main__":
    main()