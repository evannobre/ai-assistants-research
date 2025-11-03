#!/usr/bin/env python3
"""
FASTA File Generator
Generates FASTA format files with specified length for testing regex-redux
"""

import sys
import random

def generate_fasta(length):
    """Generate FASTA format data with specified total sequence length"""
    
    # DNA nucleotides
    nucleotides = ['A', 'T', 'G', 'C']
    
    # FASTA header
    print(">ONE Homo sapiens alu")
    
    # Generate random DNA sequence
    sequence_length = 0
    line_length = 60  # Standard FASTA line length
    
    while sequence_length < length:
        # Generate a line of sequence
        line = ''
        for _ in range(min(line_length, length - sequence_length)):
            line += random.choice(nucleotides)
            sequence_length += 1
        
        print(line)
        
        # Occasionally add another header to make it more realistic
        if sequence_length < length and random.random() < 0.001:
            print(f">TWO Homo sapiens sequence {sequence_length}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fasta_generator.py <length>", file=sys.stderr)
        print("Example: python3 fasta_generator.py 5000000 > input5000000.txt", file=sys.stderr)
        sys.exit(1)
    
    try:
        length = int(sys.argv[1])
        if length <= 0:
            raise ValueError("Length must be positive")
    except ValueError as e:
        print(f"Error: Invalid length argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    generate_fasta(length)

if __name__ == "__main__":
    main()