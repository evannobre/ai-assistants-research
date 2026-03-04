#!/usr/bin/env python3
import sys

def reverse_complement(dna: str) -> str:
    """
    Compute the reverse complement of a DNA sequence.
    
    The function maps each nucleotide to its complement using a dictionary
    and reverses the sequence to simulate the reverse complement process.
    
    Parameters:
        dna (str): The DNA sequence (expected to contain only 'A', 'T', 'C', 'G').
    
    Returns:
        str: The reverse complement of the DNA sequence.
    """
    # Mapping of each nucleotide to its complement
    complement_mapping = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C'
    }
    
    # Reverse the sequence and generate its complement
    rev_comp = ''.join(complement_mapping.get(base, base) for base in dna[::-1])
    return rev_comp

def main():
    """
    Main function to read the DNA sequence from the command line,
    validate it, and output its reverse complement.
    
    Usage:
        python3 reverse_complement.py ATGCATGCA
    """
    # Check that a single DNA sequence argument is provided
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <DNA sequence>")
        sys.exit(1)
    
    # Normalize the input by converting to uppercase
    dna = sys.argv[1].upper()
    
    # Validate that the sequence only contains valid nucleotides: A, T, C, G.
    valid_bases = {'A', 'T', 'C', 'G'}
    for base in dna:
        if base not in valid_bases:
            print("Error: DNA sequence can only contain the characters A, T, C, and G.")
            sys.exit(1)
    
    # Compute the reverse complement and print the result
    result = reverse_complement(dna)
    print("Reverse Complement:", result)

if __name__ == '__main__':
    main()
