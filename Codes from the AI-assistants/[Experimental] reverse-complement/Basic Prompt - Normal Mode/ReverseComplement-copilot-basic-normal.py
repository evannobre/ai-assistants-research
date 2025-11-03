import sys

def reverse_complement(dna_sequence: str) -> str:
    """Returns the reverse complement of the given DNA sequence."""
    complement_map = str.maketrans("ATGC", "TACG")  # Native translation mapping
    return dna_sequence.translate(complement_map)[::-1]  # Complement + Reverse

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <DNA_sequence>")
        sys.exit(1)

    input_sequence = sys.argv[1].upper()  # Ensure uppercase input
    result = reverse_complement(input_sequence)
    print(f"Reverse Complement: {result}")
