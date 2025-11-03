import sys
from itertools import islice
from typing import Iterator

def lcg(seed: int, a: int = 1664525, c: int = 1013904223, m: int = 2**32) -> Iterator[int]:
    """Linear Congruential Generator yielding pseudorandom numbers."""
    while True:
        seed = (a * seed + c) % m
        yield seed

def generate_sequence(seed: int, length: int) -> str:
    """Generate a DNA sequence using LCG."""
    bases = ['A', 'T', 'C', 'G']
    rand_gen = lcg(seed)
    # Use bitwise AND with 3 (0b11) to get 0-3 range
    sequence = (bases[(next(rand_gen) & 3] for _ in range(length))
    return ''.join(sequence)

def fasta_simulation(output_file: str, num_seqs: int, seq_length: int, seed: int = 42):
    """Generate multiple FASTA sequences using LCG."""
    rand_seed_gen = lcg(seed)
    
    with open(output_file, 'w') as f:
        for i in range(1, num_seqs + 1):
            # Get a new seed for each sequence from our master LCG
            seq_seed = next(rand_seed_gen)
            sequence = generate_sequence(seq_seed, seq_length)
            
            # Write FASTA record
            f.write(f">seq_{i}_seed_{seq_seed}\n")
            
            # Write sequence in lines of 80 characters (FASTA convention)
            for chunk in (sequence[j:j+80] for j in range(0, len(sequence), 80)):
                f.write(f"{chunk}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python lcg_fasta.py <num_seqs> <seq_length> <output_file>")
        sys.exit(1)
    
    num_seqs = int(sys.argv[1])
    seq_length = int(sys.argv[2])
    output_file = sys.argv[3]
    
    fasta_simulation(output_file, num_seqs, seq_length)