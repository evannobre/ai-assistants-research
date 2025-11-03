#!/usr/bin/env python3
"""
FASTA Simulation using Naïve Linear Congruential Generator
This implementation uses native Python libraries for maximum performance
and compatibility with the original FASTA benchmark specifications.
"""

import sys
import array
from typing import List, Tuple


class NaiveLCG:
    """
    Naïve Linear Congruential Generator implementation
    Uses the same parameters as the original FASTA benchmark:
    - Multiplier (a): 3877
    - Increment (c): 29573  
    - Modulus (m): 139968 (2^17 - 2^7)
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.current = seed
        # LCG parameters from original FASTA benchmark
        self.a = 3877      # multiplier
        self.c = 29573     # increment  
        self.m = 139968    # modulus (2^17 - 2^7)
        self.inv_m = 1.0 / self.m  # precompute for performance
    
    def next_random(self) -> float:
        """Generate next pseudorandom number in range [0, 1)"""
        self.current = (self.a * self.current + self.c) % self.m
        return self.current * self.inv_m
    
    def reset(self, seed: int = None):
        """Reset generator to initial or new seed"""
        if seed is not None:
            self.seed = seed
        self.current = self.seed


class FASTASimulator:
    """
    FASTA sequence simulation using LCG for pseudorandom generation
    Implements both repeat and random sequence generation algorithms
    """
    
    # Amino acid frequency table (simplified protein model)
    AMINO_ACIDS = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]
    
    # DNA nucleotide frequency table  
    DNA_NUCLEOTIDES = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    
    def __init__(self, seed: int = 42):
        self.lcg = NaiveLCG(seed)
        self.line_length = 60  # FASTA standard line length
        
        # Precompute cumulative probability tables for faster lookup
        self.amino_cumulative = self._build_cumulative_table(self.AMINO_ACIDS)
        self.dna_cumulative = self._build_cumulative_table(self.DNA_NUCLEOTIDES)
    
    def _build_cumulative_table(self, freq_table: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Build cumulative probability table for efficient random selection"""
        cumulative = []
        total = 0.0
        for char, freq in freq_table:
            total += freq
            cumulative.append((char, total))
        return cumulative
    
    def _select_weighted_random(self, cumulative_table: List[Tuple[str, float]]) -> str:
        """Select character based on weighted probabilities using LCG"""
        rand_val = self.lcg.next_random()
        
        # Binary search for efficiency with larger alphabets
        left, right = 0, len(cumulative_table) - 1
        while left < right:
            mid = (left + right) // 2
            if cumulative_table[mid][1] < rand_val:
                left = mid + 1
            else:
                right = mid
        
        return cumulative_table[left][0]
    
    def generate_repeat_sequence(self, sequence: str, length: int, description: str = "Repeat sequence"):
        """
        Generate FASTA repeat sequence by cycling through a given pattern
        Uses native string operations for maximum performance
        """
        print(f">{description}")
        
        seq_len = len(sequence)
        chars_written = 0
        line_buffer = array.array('u')  # Unicode character array for efficiency
        
        for i in range(length):
            char = sequence[i % seq_len]
            line_buffer.append(char)
            chars_written += 1
            
            # Write line when buffer reaches line length
            if chars_written % self.line_length == 0:
                print(line_buffer.tounicode())
                line_buffer = array.array('u')
        
        # Write remaining characters
        if line_buffer:
            print(line_buffer.tounicode())
    
    def generate_random_sequence(self, length: int, sequence_type: str = "dna", 
                                description: str = "Random sequence"):
        """
        Generate random FASTA sequence using LCG and weighted character selection
        
        Args:
            length: Number of characters to generate
            sequence_type: "dna" or "protein" 
            description: FASTA header description
        """
        print(f">{description}")
        
        # Select appropriate frequency table
        cumulative_table = (self.dna_cumulative if sequence_type == "dna" 
                          else self.amino_cumulative)
        
        chars_written = 0
        line_buffer = array.array('u')  # Unicode character array for efficiency
        
        for _ in range(length):
            char = self._select_weighted_random(cumulative_table)
            line_buffer.append(char)
            chars_written += 1
            
            # Write line when buffer reaches line length  
            if chars_written % self.line_length == 0:
                print(line_buffer.tounicode())
                line_buffer = array.array('u')
        
        # Write remaining characters
        if line_buffer:
            print(line_buffer.tounicode())
    
    def run_fasta_benchmark(self, n: int):
        """
        Run the complete FASTA benchmark simulation
        Generates three sequences as per original specification:
        1. Repeat sequence (2*n length)
        2. Random DNA sequence (3*n length) 
        3. Random protein sequence (5*n length)
        """
        
        # Sequence 1: Repeat sequence
        repeat_seq = ("GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
                     "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
                     "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
                     "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
                     "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
                     "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
                     "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA")
        
        print("Running FASTA simulation with naïve LCG...")
        print(f"Sequence length parameter: {n}")
        print()
        
        # Generate repeat sequence (2*n characters)
        self.generate_repeat_sequence(
            repeat_seq, 
            2 * n, 
            f"ONE Homo sapiens alu (2*{n}={2*n} bp)"
        )
        print()
        
        # Reset LCG for reproducible results
        self.lcg.reset()
        
        # Generate random DNA sequence (3*n characters)
        self.generate_random_sequence(
            3 * n, 
            "dna",
            f"TWO IUB ambiguity codes (3*{n}={3*n} bp)"
        )
        print()
        
        # Generate random protein sequence (5*n characters)  
        self.generate_random_sequence(
            5 * n,
            "protein", 
            f"THREE Homo sapiens frequency (5*{n}={5*n} bp)"
        )


def main():
    """Main function with command line argument handling"""
    # Default sequence length
    n = 1000
    
    # Parse command line argument if provided
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
            if n <= 0:
                raise ValueError("Sequence length must be positive")
        except ValueError as e:
            print(f"Error: Invalid sequence length. {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create simulator and run benchmark
    simulator = FASTASimulator(seed=42)
    simulator.run_fasta_benchmark(n)


if __name__ == "__main__":
    main()