import sys
from pathlib import Path

def get_reverse_complement(sequence):
    # Native translation table: maps each base to its complement
    # Includes support for N (unknown) and lowercase
    trans_table = str.maketrans(
        "ATCGNatcgn",
        "TAGCNtagcn"
    )
    
    # 1. Complement the sequence using the table
    # 2. Reverse the string using slicing [::-1]
    return sequence.translate(trans_table)[::-1]

def main():
    # Check if a filename was provided via command line
    if len(sys.argv) < 2:
        print("Usage: python rev_comp.py <dna_file.txt>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    # Reading and processing
    try:
        with file_path.open("r") as f:
            # We strip whitespace to handle trailing newlines
            raw_data = f.read().strip()
            
            # Handle FASTA format vs raw sequence
            if raw_data.startswith(">"):
                header, *lines = raw_data.splitlines()
                sequence = "".join(lines)
                result = get_reverse_complement(sequence)
                print(f"{header}_reverse_complement\n{result}")
            else:
                print(get_reverse_complement(raw_data))
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()