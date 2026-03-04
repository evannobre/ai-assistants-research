import argparse
import sys
import os

def get_reverse_complement(dna_sequence):
    """
    Computes the reverse complement of a DNA sequence using 
    native string translation tables for efficiency.
    """
    # 1. Create the translation table (Complement step)
    #    A->T, T->A, C->G, G->C, N->N (case insensitive handling)
    #    We map both upper and lower case to ensure robustness.
    trans_table = str.maketrans(
        "ATCGNatcgn", 
        "TAGCNtagcn"
    )
    
    # 2. Translate (Complement) and then Reverse (Slice [::-1])
    #    Note: Doing the lookup first and then reversing is often 
    #    slightly faster in Python than reversing then looking up.
    return dna_sequence.translate(trans_table)[::-1]

def read_file(file_path):
    """
    Reads a file and returns the raw sequence, stripping newlines/headers.
    Basic support for FASTA (skips lines starting with >).
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)

    sequence_parts = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or FASTA headers
                if not line or line.startswith(">"):
                    continue
                sequence_parts.append(line)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    return "".join(sequence_parts)

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Calculate the Reverse Complement of a DNA sequence file."
    )
    parser.add_argument(
        "file", 
        help="Path to the input text file containing the DNA sequence."
    )
    
    args = parser.parse_args()
    
    # Process
    raw_dna = read_file(args.file)
    result = get_reverse_complement(raw_dna)
    
    # Output result
    print("--- Original Sequence (First 50 chars) ---")
    print(raw_dna[:50] + ("..." if len(raw_dna) > 50 else ""))
    print("\n--- Reverse Complement ---")
    print(result)

if __name__ == "__main__":
    main()