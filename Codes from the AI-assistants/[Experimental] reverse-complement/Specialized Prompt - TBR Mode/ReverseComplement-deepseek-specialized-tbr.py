import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 reverse_complement.py <dna_sequence>")
        sys.exit(1)
    
    seq = sys.argv[1].replace(" ", "").upper()
    
    if not seq:
        print("Error: DNA sequence is empty after removing spaces.")
        sys.exit(1)
    
    valid_bases = set('ACGT')
    if any(char not in valid_bases for char in seq):
        print("Error: DNA sequence can only contain A, C, G, T (case insensitive).")
        sys.exit(1)
    
    trans_table = str.maketrans('ACGT', 'TGCA')
    reverse_complement = seq[::-1].translate(trans_table)
    print(reverse_complement)

if __name__ == "__main__":
    main()