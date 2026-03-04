import sys
import itertools
from typing import List, Tuple

class NaiveLCG:
    """Naïve Linear Congruential Generator without caching"""
    IM = 139968
    IA = 3877
    IC = 29573
    _seed = 42
    
    @classmethod
    def random(cls, max_val: float) -> float:
        """Generate random number as specified in requirements"""
        cls._seed = (cls._seed * cls.IA + cls.IC) % cls.IM
        return max_val * cls._seed / cls.IM
    
    @classmethod
    def reset_seed(cls):
        """Reset seed to initial value"""
        cls._seed = 42

class FastaSimulation:
    """FASTA simulation using naïve LCG and cumulative probabilities"""
    
    # ALU sequence for copying
    ALU_SEQUENCE = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    
    # Alphabet 1: Homo sapiens frequencies
    ALPHABET_1 = [
        ('a', 0.27),
        ('c', 0.12),
        ('g', 0.12),
        ('t', 0.27)
    ]
    
    # Alphabet 2: IUB ambiguity codes
    ALPHABET_2 = [
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
    
    @staticmethod
    def _compute_cumulative_probabilities(probs: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Convert probabilities to cumulative probabilities"""
        cumulative = []
        running_sum = 0.0
        for char, prob in probs:
            running_sum += prob
            cumulative.append((char, running_sum))
        return cumulative
    
    @staticmethod
    def _select_nucleotide_linear_search(cumulative: List[Tuple[str, float]], 
                                        random_val: float) -> str:
        """Select nucleotide using linear search on cumulative probabilities"""
        for char, cum_prob in cumulative:
            if random_val <= cum_prob:
                return char
        return cumulative[-1][0]  # Should never happen if cumulative sums to 1
    
    @classmethod
    def _generate_alu_sequence(cls, length: int) -> str:
        """Generate DNA sequence by copying from ALU sequence"""
        result = []
        alu_len = len(cls.ALU_SEQUENCE)
        for i in range(length):
            result.append(cls.ALU_SEQUENCE[i % alu_len])
        return ''.join(result)
    
    @classmethod
    def _generate_random_sequence(cls, alphabet: List[Tuple[str, float]], 
                                 length: int) -> str:
        """Generate DNA sequence using weighted random selection"""
        # Compute cumulative probabilities
        cumulative = cls._compute_cumulative_probabilities(alphabet)
        
        # Generate sequence
        result = []
        for _ in range(length):
            # Generate fresh random number using naïve LCG
            random_val = NaiveLCG.random(1.0)
            # Select nucleotide using linear search
            nucleotide = cls._select_nucleotide_linear_search(cumulative, random_val)
            result.append(nucleotide)
        
        return ''.join(result)
    
    @classmethod
    def generate_fasta(cls, n: int, output_file=sys.stdout):
        """Generate complete FASTA output as specified"""
        # Reset seed for reproducibility
        NaiveLCG.reset_seed()
        
        # Part 1: Homo sapiens alu
        output_file.write(f">ONE Homo sapiens alu\n")
        seq1 = cls._generate_alu_sequence(n * 2)
        for i in range(0, len(seq1), 60):
            output_file.write(seq1[i:i+60] + "\n")
        
        # Part 2: IUB ambiguity codes (using alphabet 2)
        output_file.write(f">TWO IUB ambiguity codes\n")
        seq2 = cls._generate_random_sequence(cls.ALPHABET_2, n * 3)
        for i in range(0, len(seq2), 60):
            output_file.write(seq2[i:i+60] + "\n")
        
        # Part 3: Homo sapiens alu (using alphabet 1)
        output_file.write(f">THREE Homo sapiens alu\n")
        seq3 = cls._generate_random_sequence(cls.ALPHABET_1, n * 5)
        for i in range(0, len(seq3), 60):
            output_file.write(seq3[i:i+60] + "\n")

def main():
    """Main function to run FASTA simulation"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number>")
        print("Example: python3 fasta.py 1000")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
        
        # Use larger argument for performance testing
        if n == 25000000:
            print(f"Running performance test with n={n:,}...", file=sys.stderr)
            print(f"Total sequence length: {n*10:,} characters", file=sys.stderr)
        
        FastaSimulation.generate_fasta(n)
        
    except ValueError:
        print("Error: Argument must be a positive integer", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()