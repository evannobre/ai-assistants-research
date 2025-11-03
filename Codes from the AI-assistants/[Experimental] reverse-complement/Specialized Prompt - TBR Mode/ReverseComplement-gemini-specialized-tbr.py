import sys

def get_reverse_complement(dna_sequence: str) -> str:
    """
    Calculates the reverse complement of a given DNA sequence.

    Args:
        dna_sequence: A string representing the DNA sequence.
                      Valid characters are A, T, C, G (case-insensitive).

    Returns:
        A string representing the reverse complement of the input DNA sequence.
        Returns an error message string if the input is invalid.
    """
    # --- Validation ---
    if not dna_sequence:
        return "Error: Input DNA sequence cannot be empty."

    valid_chars = "ATCG"
    # Convert to uppercase for consistent processing and validation
    processed_sequence = dna_sequence.upper()

    for char in processed_sequence:
        if char not in valid_chars:
            return f"Error: Invalid character '{char}' found in DNA sequence. Only A, T, C, G are allowed."

    # --- Step 1: Reverse the sequence ---
    # Python's slicing [::-1] is a very efficient way to reverse a string
    reversed_sequence = processed_sequence[::-1]

    # --- Step 2: Complement the sequence ---
    # Using a dictionary for mapping complements is clear and efficient
    complement_map = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C'
    }

    # Using a list comprehension and str.join() is generally efficient for building strings
    complemented_sequence = "".join([complement_map[nucleotide] for nucleotide in reversed_sequence])

    return complemented_sequence

if __name__ == "__main__":
    # --- Command-line argument handling ---
    if len(sys.argv) != 2:
        print("Usage: python reverse_complement.py <DNA_SEQUENCE>")
        print("Example: python reverse_complement.py ATGCGTA")
        sys.exit(1) # Exit with an error code

    input_sequence = sys.argv[1]
    result = get_reverse_complement(input_sequence)

    if result.startswith("Error:"):
        print(result, file=sys.stderr) # Print errors to standard error
        sys.exit(1) # Exit with an error code
    else:
        print(f"Original Sequence:   {input_sequence.upper()}")
        print(f"Reverse Complement: {result}")