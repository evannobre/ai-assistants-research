#!/usr/bin/env python3
import argparse

def reverse_complement(seq: str) -> str:
    """
    Return the reverse complement of the given DNA sequence.

    Args:
        seq (str): A DNA sequence (e.g., "ATGCGT").

    Returns:
        str: The reverse complement of the sequence.

    Raises:
        ValueError: If the sequence contains an invalid nucleotide.
    """
    # Define the complement mapping for nucleotides.
    complement_map = {
        'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
        'a': 't', 't': 'a', 'c': 'g', 'g': 'c'
    }
    
    # Reverse the sequence using slicing.
    reversed_seq = seq[::-1]
    
    # Build the reverse complement by transforming each nucleotide.
    try:
        rev_complement = ''.join(complement_map[nuc] for nuc in reversed_seq)
    except KeyError as error:
        raise ValueError(f"Invalid nucleotide found: {error.args[0]} in sequence '{seq}'")
    
    return rev_complement

def main():
    # Use argparse to get the DNA sequence from the command line.
    parser = argparse.ArgumentParser(description="Reverse Complement Simulator for DNA Sequences")
    parser.add_argument("sequence", help="DNA sequence to be complemented (e.g., ATGCGT)", type=str)
    args = parser.parse_args()

    try:
        result = reverse_complement(args.sequence)
        print("Reverse Complement:", result)
    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
