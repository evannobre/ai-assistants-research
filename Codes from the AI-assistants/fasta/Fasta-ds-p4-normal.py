#!/usr/bin/env python3
import sys
import array
from typing import List, Tuple

# LCG constants as specified
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def lcg_random(max_val: float) -> float:
    """Naïve Linear Congruential Generator as specified"""
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

class FastaSimulation:
    def __init__(self):
        # Alphabet definitions
        self.iub_alphabet = [
            ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
            ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
            ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
            ('V', 0.02), ('W', 0.02), ('Y', 0.02)
        ]
        
        self.homosapiens_alphabet = [
            ('a', 0.3029549426680),
            ('c', 0.1979883004921),
            ('g', 0.1975473066391),
            ('t', 0.3015094502008)
        ]
        
        # Precompute cumulative probabilities
        self.iub_cumulative = self._build_cumulative(self.iub_alphabet)
        self.homosapiens_cumulative = self._build_cumulative(self.homosapiens_alphabet)
    
    def _build_cumulative(self, alphabet: List[Tuple[str, float]]) -> List[Tuple[float, str]]:
        """Build cumulative probabilities without optimization"""
        cumulative = []
        total = 0.0
        for char, prob in alphabet:
            total += prob
            cumulative.append((total, char))
        return cumulative
    
    def _select_nucleotide(self, cumulative: List[Tuple[float, str]]) -> str:
        """Select nucleotide using linear search against cumulative probabilities"""
        r = lcg_random(1.0)
        
        # Naïve linear search as specified
        for cum_prob, char in cumulative:
            if r <= cum_prob:
                return char
        
        # Fallback (should never happen with proper probabilities)
        return cumulative[-1][1]
    
    def make_random_fasta(self, 
                         identifier: str, 
                         desc: str, 
                         alphabet_cumulative: List[Tuple[float, str]],
                         n: int) -> None:
        """Generate DNA sequences by weighted random selection"""
        # Use sys.stdout.write for better performance
        sys.stdout.write(f">{identifier} {desc}\n")
        
        # Use array for efficient character storage
        line_buffer = array.array('u', ' ' * 60)
        
        chars_remaining = n
        while chars_remaining > 0:
            line_length = min(60, chars_remaining)
            
            # Build line character by character
            for i in range(line_length):
                line_buffer[i] = self._select_nucleotide(alphabet_cumulative)
            
            # Write the line
            sys.stdout.write(line_buffer.tounicode()[:line_length] + '\n')
            chars_remaining -= line_length
    
    def make_repeat_fasta(self, identifier: str, desc: str, sequence: str, n: int) -> None:
        """Generate DNA sequences by copying from given sequence"""
        sys.stdout.write(f">{identifier} {desc}\n")
        
        seq_len = len(sequence)
        chars_remaining = n
        
        # Use array for efficient repeated access
        seq_array = array.array('u', sequence)
        
        while chars_remaining > 0:
            line_length = min(60, chars_remaining)
            
            # Build line by wrapping around the sequence
            line = []
            seq_pos = (n - chars_remaining) % seq_len
            
            for _ in range(line_length):
                line.append(seq_array[seq_pos])
                seq_pos = (seq_pos + 1) % seq_len
            
            sys.stdout.write(''.join(line) + '\n')
            chars_remaining -= line_length

def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 1000  # Default
    
    # Reset seed for reproducibility
    global SEED
    SEED = 42
    
    sim = FastaSimulation()
    
    # ALU sequence for repeat FASTA
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    
    # Generate output
    sim.make_repeat_fasta("ONE", "Homo sapiens alu", alu, n * 2)
    sim.make_random_fasta("TWO", "IUB ambiguity codes", sim.iub_cumulative, n * 3)
    sim.make_random_fasta("THREE", "Homo sapiens frequency", sim.homosapiens_cumulative, n * 5)

if __name__ == "__main__":
    main()