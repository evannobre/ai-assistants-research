import numpy as np
import os
from typing import BinaryIO
import sys
from math import gcd

class FASTASimulatorLCG:
    """
    FASTA sequence simulator using a naïve Linear Congruential Generator (LCG)
    for efficient pseudorandom number generation.
    
    Optimized for:
    - Ubuntu 24.04.2 LTS 64-bit
    - 16GB vRAM
    - 30GB SSD storage
    """
    
    def __init__(self, seed: int = 1):
        """
        Initialize LCG parameters (using parameters from glibc)
        a = multiplier
        c = increment
        m = modulus (2^64 for 64-bit systems)
        """
        self.seed = seed
        self.a = 6364136223846793005
        self.c = 1
        self.m = 1 << 64  # 2^64 for 64-bit systems
        
        # Nucleotide probabilities (human genome approx)
        self.nuc_probs = {
            'A': 0.29,
            'C': 0.21,
            'G': 0.21,
            'T': 0.29
        }
        
        # Precompute cumulative probabilities for faster generation
        self._precompute_cumulative()
        
    def _precompute_cumulative(self):
        """Precompute cumulative probabilities for faster sampling"""
        self.cumulative = []
        self.nucleotides = []
        cum_prob = 0.0
        
        for nuc, prob in sorted(self.nuc_probs.items()):
            cum_prob += prob
            self.cumulative.append(cum_prob)
            self.nucleotides.append(nuc)
        
        # Normalize to account for any floating-point errors
        self.cumulative[-1] = 1.0
    
    def _lcg(self) -> float:
        """Generate next pseudorandom number in [0, 1) using LCG"""
        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed / self.m
    
    def generate_sequence(self, length: int) -> str:
        """Generate a random nucleotide sequence of given length"""
        # Use numpy for vectorized operations when sequence is large
        if length > 1_000_000:
            return self._generate_large_sequence(length)
        
        # For smaller sequences, use Python native implementation
        sequence = []
        for _ in range(length):
            rand_val = self._lcg()
            # Find which nucleotide this random value corresponds to
            for i, cum_prob in enumerate(self.cumulative):
                if rand_val < cum_prob:
                    sequence.append(self.nucleotides[i])
                    break
        return ''.join(sequence)
    
    def _generate_large_sequence(self, length: int) -> str:
        """Optimized generation for large sequences (>1M bases)"""
        # Generate all random numbers at once (memory efficient)
        rand_vals = np.empty(length, dtype=np.float64)
        for i in range(length):
            rand_vals[i] = self._lcg()
        
        # Vectorized nucleotide selection
        bins = np.array(self.cumulative)
        indices = np.digitize(rand_vals, bins)
        sequence = np.take(self.nucleotides, indices)
        
        return ''.join(sequence)
    
    def generate_fasta(
        self,
        output_path: str,
        seq_length: int,
        seq_count: int = 1,
        chunk_size: int = 10_000_000,
        compress: bool = False
    ) -> None:
        """
        Generate FASTA file with simulated sequences.
        
        Args:
            output_path: Path to output file
            seq_length: Length of each sequence
            seq_count: Number of sequences to generate
            chunk_size: Write sequences in chunks to conserve memory
            compress: If True, output will be gzipped
        """
        if compress:
            import gzip
            opener = gzip.open
            mode = 'wt'
        else:
            opener = open
            mode = 'w'
        
        with opener(output_path, mode) as f:
            for seq_num in range(1, seq_count + 1):
                # Write header
                f.write(f">sequence_{seq_num}\n")
                
                # Write sequence in chunks to conserve memory
                for chunk_start in range(0, seq_length, chunk_size):
                    chunk_end = min(chunk_start + chunk_size, seq_length)
                    chunk_length = chunk_end - chunk_start
                    
                    # Generate and write chunk
                    chunk = self.generate_sequence(chunk_length)
                    
                    # Write in FASTA format (60 chars per line)
                    for line_start in range(0, len(chunk), 60):
                        line_end = min(line_start + 60, len(chunk))
                        f.write(chunk[line_start:line_end] + '\n')

def validate_environment():
    """Validate system meets requirements"""
    # Check Python version
    if sys.version_info < (3, 8):
        raise RuntimeError("Python 3.8 or later is required")
    
    # Check available memory (rough estimate)
    mem_info = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    if mem_info < 12 * (1024**3):  # Less than 12GB RAM
        print("Warning: System has less than 12GB RAM - large sequences may cause issues")
    
    # Check disk space
    stat = os.statvfs('/')
    free_space = stat.f_frsize * stat.f_bavail
    if free_space < 5 * (1024**3):  # Less than 5GB free
        print("Warning: Less than 5GB disk space available")

if __name__ == "__main__":
    validate_environment()
    
    # Example usage
    simulator = FASTASimulatorLCG(seed=42)
    
    # Generate a small test file
    simulator.generate_fasta("test.fasta", seq_length=1000, seq_count=5)
    
    # Generate a large compressed file (1GB uncompressed)
    print("Generating large FASTA file...")
    simulator.generate_fasta(
        "large_sequences.fasta.gz",
        seq_length=100_000_000,
        seq_count=1,
        compress=True
    )
    print("Done!")