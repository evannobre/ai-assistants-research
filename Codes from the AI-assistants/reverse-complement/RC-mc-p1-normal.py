import sys

def reverse_complement(seq):
    comp = str.maketrans("ACGTacgt", "TGCAtgca")
    return seq.translate(comp)[::-1]

def main():
    if len(sys.argv) != 2:
        print("Usage: python reverse_complement.py <dna_file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r") as f:
            dna = f.read().strip()
    except FileNotFoundError:
        print("Error: file not found")
        sys.exit(1)

    print(reverse_complement(dna))

if __name__ == "__main__":
    main()
