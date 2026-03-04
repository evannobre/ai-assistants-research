import sys

def reverse_complement(dna_sequence):
    """
    Computes the reverse complement of a DNA sequence.

    Args:
        dna_sequence: A string representing the DNA sequence.
                       Valid characters are 'A', 'C', 'G', 'T' (case-insensitive).

    Returns:
        A string representing the reverse complement of the input DNA sequence,
        or None if the input is invalid.
    """
    valid_chars = "ACGT"
    # Convert to uppercase and check for invalid characters
    sequence_upper = dna_sequence.upper()
    if not all(char in valid_chars for char in sequence_upper):
        print("Error: Invalid characters in DNA sequence. Only A, C, G, T are allowed.")
        return None

    # Reverse the sequence
    reversed_sequence = sequence_upper[::-1]

    # Create the complement
    complement_map = str.maketrans("ACGT", "TGCA")
    complement_sequence = reversed_sequence.translate(complement_map)

    return complement_sequence

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <DNA_SEQUENCE>")
        sys.exit(1)

    input_sequence = sys.argv[1]
    result = reverse_complement(input_sequence)

    if result:
        print(f"Original Sequence: {input_sequence.upper()}")
        print(f"Reverse Complement: {result}")