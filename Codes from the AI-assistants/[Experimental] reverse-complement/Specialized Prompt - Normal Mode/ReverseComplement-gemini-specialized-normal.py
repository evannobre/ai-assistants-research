import sys

def reverse_complement(dna_sequence: str) -> str:
    """
    Computes the reverse complement of a DNA sequence.

    Args:
        dna_sequence: The input DNA sequence string (e.g., "AGCT").

    Returns:
        The reverse complement DNA sequence string (e.g., "AGCT" -> "AGCT").
        Returns an empty string if the input is empty or invalid characters are present.
    """
    # 1. Define Complement Mapping (using a dictionary for O(1) lookup)
    # This is a core 'native' data structure.
    complement_map = {
        'A': 'T', 'a': 'T',
        'T': 'A', 't': 'A',
        'C': 'G', 'c': 'G',
        'G': 'C', 'g': 'C',
        'N': 'N', 'n': 'N' # Handle unknown bases gracefully, as per standard practice
    }

    # Input validation: Ensure the sequence only contains valid DNA bases.
    # While not strictly required by the prompt, good practice for robustness.
    # We convert to uppercase for mapping simplicity and then revert if needed.
    # Here, we'll just accept 'A', 'T', 'C', 'G', 'N' (case-insensitive)
    upper_dna_sequence = dna_sequence.upper()
    for base in upper_dna_sequence:
        if base not in complement_map:
            print(f"Error: Invalid DNA base '{base}' found in sequence.", file=sys.stderr)
            return "" # Or raise an exception, depending on error handling strategy

    # 2. Reverse Sequence
    # Python's slicing provides a very efficient and 'native' way to reverse a string.
    # This operation creates a new string in reverse.
    reversed_sequence = upper_dna_sequence[::-1]

    # 3. Complement Bases
    # Using a list comprehension for efficiency and readability to build the new sequence.
    # This is also a highly optimized operation in Python.
    complement_bases = [complement_map[base] for base in reversed_sequence]

    # 4. Join the list of characters back into a string.
    # This is efficient for concatenating many characters.
    reverse_complement_sequence = "".join(complement_bases)

    return reverse_complement_sequence

def main():
    """
    Main function to handle command-line arguments and run the simulation.
    """
    # Check if a DNA sequence was provided as a command-line argument.
    if len(sys.argv) < 2:
        print("Usage: python reverse_complement.py <DNA_SEQUENCE>", file=sys.stderr)
        print("Example: python reverse_complement.py AGCT", file=sys.stderr)
        sys.exit(1) # Exit with an error code

    dna_sequence = sys.argv[1]

    print(f"Input DNA Sequence: {dna_sequence}")
    result = reverse_complement(dna_sequence)

    if result: # Only print if the result is not an empty string (i.e., no error)
        print(f"Reverse Complement: {result}")
    else:
        sys.exit(1) # Exit with an error if there was an issue

if __name__ == "__main__":
    main()