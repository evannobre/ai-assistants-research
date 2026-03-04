import sys

def reverse_complement(dna_sequence: str) -> str:
    """
    Computes the reverse complement of a DNA sequence.

    Args:
        dna_sequence: The input DNA string (e.g., "ATGC").

    Returns:
        The reverse complement string (e.g., "GCAT").
    """
    # Convert to uppercase to handle mixed case input
    dna_sequence = dna_sequence.upper()

    # Step 1: Reverse the sequence
    reversed_sequence = dna_sequence[::-1]

    # Step 2: Complement the sequence
    complement_map = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C',
        'N': 'N'  # Assuming N (unknown) maps to N
    }

    complemented_sequence = ""
    for base in reversed_sequence:
        complemented_sequence += complement_map.get(base, base) # Get complement or keep original if not found

    return complemented_sequence

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <DNA_SEQUENCE>")
        print("Example: python script_name.py ATGCGTAG")
        sys.exit(1) # Exit with an error code

    input_sequence = sys.argv[1]

    # Basic validation for typical DNA characters (optional, can be more robust)
    valid_chars = "ATCGN"
    if not all(char.upper() in valid_chars for char in input_sequence):
        print(f"Error: Input sequence '{input_sequence}' contains invalid characters.")
        print("Valid characters are A, T, C, G, N (case-insensitive).")
        sys.exit(1)

    rev_comp_sequence = reverse_complement(input_sequence)

    print(f"Original Sequence: {input_sequence.upper()}")
    print(f"Reverse Complement: {rev_comp_sequence}")