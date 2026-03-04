import sys
import random
import itertools
import math
from typing import List, Tuple, Optional

class NaiveLCG:
    """Naïve Linear Congruential Generator"""
    def __init__(self, seed: int = None):
        # Standard LCG parameters (like glibc)
        self.a = 1103515245
        self.c = 12345
        self.m = 2**31
        self.state = seed if seed is not None else random.randint(0, 2**31-1)
    
    def rand_int(self, max_val: Optional[int] = None) -> int:
        """Generate random integer [0, m-1] or [0, max_val-1]"""
        self.state = (self.a * self.state + self.c) % self.m
        if max_val is not None:
            return self.state % max_val
        return self.state
    
    def random(self) -> float:
        """Generate random float in [0, 1)"""
        return self.rand_int() / self.m

class FASTAWriter:
    """FASTA format writer"""
    LINE_WIDTH = 60
    
    @staticmethod
    def write_sequence(header: str, sequence: str) -> str:
        """Format a sequence in FASTA format"""
        fasta = f">{header}\n"
        for i in range(0, len(sequence), FASTAWriter.LINE_WIDTH):
            fasta += sequence[i:i+FASTAWriter.LINE_WIDTH] + "\n"
        return fasta

class FASTAProbabilityTable:
    """Probability tables for different sequence types"""
    
    @staticmethod
    def get_nucleotide_probs() -> List[Tuple[str, float]]:
        """Return nucleotide probabilities (A, C, G, T)"""
        return [('A', 0.27), ('C', 0.23), ('G', 0.23), ('T', 0.27)]
    
    @staticmethod
    def get_amino_acid_probs() -> List[Tuple[str, float]]:
        """Return amino acid probabilities"""
        # Using standard amino acid frequencies in proteins
        aa_probs = [
            ('A', 0.074), ('R', 0.042), ('N', 0.044), ('D', 0.059),
            ('C', 0.033), ('Q', 0.037), ('E', 0.058), ('G', 0.074),
            ('H', 0.029), ('I', 0.038), ('L', 0.076), ('K', 0.072),
            ('M', 0.018), ('F', 0.040), ('P', 0.050), ('S', 0.081),
            ('T', 0.062), ('W', 0.013), ('Y', 0.033), ('V', 0.068)
        ]
        return aa_probs
    
    @staticmethod
    def cumulative_probs(probs: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Convert probabilities to cumulative distribution"""
        cumulative = []
        total = 0.0
        for char, prob in probs:
            total += prob
            cumulative.append((char, total))
        return cumulative

class SequenceGenerator:
    """Generate biological sequences using LCG"""
    
    def __init__(self, lcg: NaiveLCG):
        self.lcg = lcg
    
    def generate_sequence(self, length: int, 
                         probs: List[Tuple[str, float]]) -> str:
        """Generate a sequence of given length using probability table"""
        cumulative_probs = FASTAProbabilityTable.cumulative_probs(probs)
        sequence = []
        
        for _ in range(length):
            r = self.lcg.random()
            for char, cum_prob in cumulative_probs:
                if r <= cum_prob:
                    sequence.append(char)
                    break
        
        return ''.join(sequence)
    
    def generate_alignment(self, num_sequences: int, 
                          lengths: Tuple[int, int],
                          seq_type: str = 'nucleotide') -> List[Tuple[str, str]]:
        """Generate multiple aligned sequences"""
        probs = (FASTAProbabilityTable.get_nucleotide_probs() 
                if seq_type == 'nucleotide' 
                else FASTAProbabilityTable.get_amino_acid_probs())
        
        # Generate reference sequence
        ref_length = random.randint(lengths[0], lengths[1])
        reference = self.generate_sequence(ref_length, probs)
        
        sequences = []
        for i in range(num_sequences):
            # Introduce some mutations
            seq = list(reference)
            mutation_rate = 0.01 + self.lcg.random() * 0.04
            
            for pos in range(len(seq)):
                if self.lcg.random() < mutation_rate:
                    # Choose different character
                    r = self.lcg.random()
                    for char, cum_prob in probs:
                        if r <= cum_prob and char != seq[pos]:
                            seq[pos] = char
                            break
            
            sequences.append((f"Seq_{i+1}", ''.join(seq)))
        
        return sequences

class FASTAStatistics:
    """Calculate statistics on FASTA sequences"""
    
    @staticmethod
    def calculate_gc_content(sequence: str) -> float:
        """Calculate GC content percentage"""
        gc = sequence.count('G') + sequence.count('C')
        return (gc / len(sequence)) * 100 if sequence else 0
    
    @staticmethod
    def calculate_sequence_stats(sequence: str, 
                               probs: List[Tuple[str, float]]) -> dict:
        """Calculate various sequence statistics"""
        stats = {
            'length': len(sequence),
            'gc_content': FASTAStatistics.calculate_gc_content(sequence)
        }
        
        # Count frequencies
        char_probs = dict(probs)
        for char in char_probs:
            freq = sequence.count(char) / len(sequence)
            stats[f'freq_{char}'] = freq
            stats[f'expected_{char}'] = char_probs[char]
            stats[f'diff_{char}'] = abs(freq - char_probs[char])
        
        return stats

def main():
    """Main simulation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate FASTA sequences using Naïve LCG')
    parser.add_argument('--seed', type=int, help='LCG seed')
    parser.add_argument('--num-sequences', type=int, default=5, help='Number of sequences')
    parser.add_argument('--min-length', type=int, default=100, help='Minimum sequence length')
    parser.add_argument('--max-length', type=int, default=500, help='Maximum sequence length')
    parser.add_argument('--seq-type', choices=['nucleotide', 'protein'], 
                       default='nucleotide', help='Sequence type')
    
    args = parser.parse_args()
    
    # Initialize LCG with given seed or random
    lcg = NaiveLCG(args.seed)
    
    # Create sequence generator
    generator = SequenceGenerator(lcg)
    
    # Generate sequences
    sequences = generator.generate_alignment(
        args.num_sequences,
        (args.min_length, args.max_length),
        args.seq_type
    )
    
    # Output FASTA format
    print(f"# Generated with LCG seed: {lcg.state}")
    print(f"# Sequence type: {args.seq_type}")
    print("#" * 50)
    
    # Get probabilities for statistics
    probs = (FASTAProbabilityTable.get_nucleotide_probs() 
            if args.seq_type == 'nucleotide' 
            else FASTAProbabilityTable.get_amino_acid_probs())
    
    # Write sequences and calculate statistics
    all_stats = []
    for header, seq in sequences:
        print(FASTAWriter.write_sequence(header, seq))
        stats = FASTAStatistics.calculate_sequence_stats(seq, probs)
        all_stats.append(stats)
    
    # Print summary statistics
    print("\n# Summary Statistics")
    print("#" * 50)
    
    avg_length = sum(s['length'] for s in all_stats) / len(all_stats)
    avg_gc = sum(s['gc_content'] for s in all_stats) / len(all_stats)
    
    print(f"Average sequence length: {avg_length:.1f}")
    print(f"Average GC content: {avg_gc:.2f}%")
    
    # Show character frequency comparison
    print("\nCharacter frequencies vs expected:")
    char_probs = dict(probs)
    chars = list(char_probs.keys())[:10]  # Show first 10
    
    for char in chars:
        avg_freq = sum(s[f'freq_{char}'] for s in all_stats) / len(all_stats)
        expected = char_probs[char]
        diff_pct = abs(avg_freq - expected) * 100
        print(f"  {char}: {avg_freq:.3f} (expected: {expected:.3f}, diff: {diff_pct:.1f}%)")

if __name__ == "__main__":
    main()