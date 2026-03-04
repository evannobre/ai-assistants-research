import sys
import os

def get_reverse_complement_stream(input_file, buffer_size=64 * 1024 * 1024):  # 64MB buffer
    """
    Efficiently processes DNA files using native translation tables.
    """
    # Native translation table (A->T, T->A, C->G, G->C, N->N)
    # Handles both upper and lower case
    trans_table = str.maketrans(
        "ATGCMRYKVHDBatgcmrykvhdb",
        "TACGKYRMBDHVtacgkyrmbdhv"
    )

    try:
        with open(input_file, 'r') as f:
            # Skip FASTA header if present
            first_line = f.readline()
            if not first_line.startswith(">"):
                f.seek(0)
            else:
                print(f"Processing sequence: {first_line.strip()}", file=sys.stderr)

            # Read remaining content
            content = f.read().replace('\n', '')
            
            # 1. Complement using native C-optimized translate
            complement = content.translate(trans_table)
            
            # 2. Reverse using slicing (highly optimized in Python)
            return complement[::-1]

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rev_comp.py <dna_file.txt>")
        sys.exit(1)

    result = get_reverse_complement_stream(sys.argv[1])
    # Print result to stdout for redirection
    print(result)