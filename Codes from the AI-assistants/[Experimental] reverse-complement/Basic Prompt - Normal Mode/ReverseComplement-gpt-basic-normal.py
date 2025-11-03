#!/usr/bin/env python3
import sys

def reverse_complement(dna: str) -> str:
    """Return the reverse complement of a DNA sequence."""
    complement_map = str.maketrans("ATCGatcg", "TAGCtagc")
    try:
        complemented = dna.translate(complement_map)
        reversed_complement = complemented[::-1]
        return reversed_complement
    except KeyError:
        raise ValueError("Invalid characters in DNA sequence")

def main():
    if len(sys.argv) != 2:
        print("Usage: reverse_complement.py <DNA_sequence>")
        sys.exit(1)

    dna_sequence = sys.argv[1]

    if not all(base in "ATCGatcg" for base in dna_sequence):
        print("Error: DNA sequence must contain only A, T, C, G (case insensitive).")
        sys.exit(2)

    result = reverse_complement(dna_sequence)
    print(f"Reverse Complement: {result}")

if __name__ == "__main__":
    main()
