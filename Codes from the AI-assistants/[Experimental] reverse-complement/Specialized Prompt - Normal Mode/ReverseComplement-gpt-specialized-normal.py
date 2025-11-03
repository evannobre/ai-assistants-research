#!/usr/bin/env python3
import sys
import argparse

def reverse_complement(dna: str) -> str:
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    try:
        reversed_comp = ''.join(complement[base] for base in reversed(dna.upper()))
    except KeyError as e:
        raise ValueError(f"Invalid DNA base found: {e.args[0]}")
    return reversed_comp

def main():
    parser = argparse.ArgumentParser(description="Reverse Complement DNA Sequence")
    parser.add_argument('sequence', type=str, help="DNA sequence (e.g. ATGCGTAC)")
    args = parser.parse_args()

    try:
        result = reverse_complement(args.sequence)
        print(f"Reverse Complement: {result}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
