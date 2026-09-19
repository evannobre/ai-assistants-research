import argparse
import sys

def reverse_complement(dna_sequence: str) -> str:
    """
    Computes the reverse complement of a DNA string.
    Handles both uppercase and lowercase nucleotides.
    """
    # 1. Define the complement mapping (including N for unknown bases)
    complement_map = str.maketrans(
        'ACGTUacgtuNn', 
        'TGCAAtgcaaNn'
    )
    
    # 2. Reverse the string using Python's slice step [::-1]
    # 3. Translate the characters using the map
    return dna_sequence[::-1].translate(complement_map)

def main():
    # Setup command-line argument parsing natively
    parser = argparse.ArgumentParser(
        description="Compute the reverse complement of a DNA sequence from a file."
    )
    parser.add_argument(
        "filepath", 
        type=str, 
        help="Path to the plain text file containing the DNA sequence"
    )
    
    args = parser.parse_args()

    try:
        with open(args.filepath, 'r') as file:
            # Read file and strip whitespace/newlines
            raw_data = file.read()
            dna = "".join(raw_data.split())
            
            if not dna:
                print("Error: The provided file is empty.", file=sys.stderr)
                sys.exit(1)

            # Compute and output
            result = reverse_complement(dna)
            print(result)
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.filepath}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()