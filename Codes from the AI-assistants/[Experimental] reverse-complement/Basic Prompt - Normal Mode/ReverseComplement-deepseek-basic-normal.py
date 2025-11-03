import sys

def reverse_complement(dna_sequence):
    """
    Compute the reverse complement of a DNA sequence using native Python.
    
    Args:
        dna_sequence (str): Input DNA sequence (case-insensitive)
    
    Returns:
        str: Reverse complement of the input sequence
    """
    # Create translation table
    complement = str.maketrans('ACGTacgt', 'TGCAtgca')
    
    # Reverse the sequence and complement each base
    return dna_sequence.translate(complement)[::-1]

def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python reverse_complement.py <DNA_SEQUENCE>")
        sys.exit(1)
    
    dna_input = sys.argv[1]
    
    # Validate input contains only DNA characters
    valid_bases = {'A', 'T', 'C', 'G', 'a', 't', 'c', 'g'}
    if not all(base in valid_bases for base in dna_input):
        print("Error: Input contains invalid DNA characters")
        sys.exit(1)
    
    # Compute and print reverse complement
    rc = reverse_complement(dna_input)
    print(f"Original: {dna_input}")
    print(f"Reverse complement: {rc}")

if __name__ == "__main__":
    main()