#!/usr/bin/env python3
"""
FASTA Generator for k-nucleotide performance testing
Usage: python3 fasta_generator.py <length> > input<length>.txt
Example: python3 fasta_generator.py 25000000 > input25000000.txt
"""

import sys
import random

# DNA nucleotides
NUCLEOTIDES = ['A', 'T', 'C', 'G']

def generate_fasta_sequence(length, seq_name="THREE"):
    """Generate a random DNA sequence in FASTA format"""
    # Header line
    print(f">{seq_name}")
    
    # Generate sequence in chunks of 60 characters (standard FASTA line length)
    line_length = 60
    
    for i in range(0, length, line_length):
        chunk_size = min(line_length, length - i)
        sequence_chunk = ''.join(random.choices(NUCLEOTIDES, k=chunk_size))
        print(sequence_chunk)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fasta_generator.py <length>", file=sys.stderr)
        print("Example: python3 fasta_generator.py 25000000 > input25000000.txt", file=sys.stderr)
        sys.exit(1)
    
    try:
        length = int(sys.argv[1])
        if length <= 0:
            raise ValueError("Length must be positive")
    except ValueError as e:
        print(f"Error: Invalid length argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Set seed for reproducible results if needed
    # random.seed(42)
    
    generate_fasta_sequence(length)

if __name__ == "__main__":
    main()